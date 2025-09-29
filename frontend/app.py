from flask import Flask, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
import os, sys, requests
from datetime import datetime
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.schema import db, User, Ticket, Order, TicketStatus, OrderStatus

# --- Setup ---
load_dotenv()
 
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key'),
    SQLALCHEMY_DATABASE_URI='sqlite:////Users/daman/Support Agent/support_agent.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=False,
    WTF_CSRF_CHECK_DEFAULT=False
)

csrf, migrate = CSRFProtect(app), Migrate(app, db)
db.init_app(app)

# --- DB & Admin Init ---
def ensure_admin():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', role='admin', is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Created default admin user')

with app.app_context():
    db.create_all()
    try:
        ensure_admin()
    except Exception as e:
        current_app.logger.error(f'DB init error: {e}')
        db.session.rollback()
        db.create_all()

# --- Auth ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username, password = StringField('Username', validators=[DataRequired()]), PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=LoginForm())

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('dashboard.html', tickets=tickets)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Helpers ---
def validate_registration(username, password, confirm_password, email):
    errors = {}
    if not username: errors['username'] = 'Username is required'
    elif len(username) < 3: errors['username'] = 'Must be at least 3 characters long'
    elif not username.replace('_', '').isalnum(): errors['username'] = 'Only letters, numbers, underscores allowed'
    if not password: errors['password'] = 'Password is required'
    elif len(password) < 6: errors['password'] = 'Must be at least 6 characters long'
    if password and password != confirm_password: errors['confirm_password'] = 'Passwords do not match'
    if email and ('@' not in email or '.' not in email): errors['email'] = 'Invalid email address'
    return errors

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        data = {f: request.form.get(f, '').strip() for f in ['username', 'password', 'confirm_password', 'email']}
        errors = validate_registration(**data)
        if User.query.filter_by(username=data['username']).first(): errors['username'] = 'Username taken'
        if data['email'] and User.query.filter_by(email=data['email']).first(): errors['email'] = 'Email registered'
        if errors:
            [flash(f"{f}: {e}", 'danger') for f, e in errors.items()]
            return render_template('register.html', **data, form_errors=errors)
        try:
            user = User(username=data['username'], email=data['email'] or None, role='user', is_active=True)
            user.set_password(data['password'])
            db.session.add(user); db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {e}')
            flash('Unexpected error, try later.', 'danger')
    return render_template('register.html', form_errors={})

@app.route('/ticket/new')
@login_required
def new_ticket(): return render_template('new_ticket.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        msg, uid = request.json.get('message', '').strip(), request.json.get('user_id', 'guest')
        if not msg: return jsonify({'response': 'Message cannot be empty'}), 400
        r = requests.post('http://127.0.0.1:8000/support/resolve', json={'user_input': msg, 'user_id': uid, 'conversation_id': f'chat_{uid}'}, timeout=30)
        if r.status_code == 200: return jsonify(r.json())
        return jsonify({'response': f'Error: {r.status_code}'}), 500
    except requests.exceptions.RequestException:
        return jsonify({'response': 'Support service unavailable.'}), 503
    except Exception as e:
        current_app.logger.error(f'Chat error: {e}')
        return jsonify({'response': 'Unexpected error.'}), 500

@app.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    t = Ticket.query.get_or_404(ticket_id)
    if t.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger'); return redirect(url_for('dashboard'))
    return render_template('view_ticket.html', ticket=t)

@app.route('/ticket/<int:ticket_id>/update-status', methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    t = Ticket.query.get_or_404(ticket_id)
    if t.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger'); return redirect(url_for('dashboard'))
    if (s := request.form.get('status')): t.status, msg = s, 'Ticket status updated.'
    else: msg = 'No status provided.'
    db.session.commit(); flash(msg, 'success' if s else 'warning')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/llm-result')
@login_required
def ticket_llm_result(ticket_id):
    return render_template('ticket_llm_result.html', ticket=Ticket.query.get_or_404(ticket_id), agent_result=request.args.get('agent_result'))

@app.route('/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    errors = {}
    if request.method == 'POST':
        try:
            product_name, product_id, amount, addr = [request.form.get(k, '').strip() for k in ['product_name','product_id','amount','shipping_address']]
            if not product_name: errors['product_name'] = 'Product name is required'
            if not product_id: errors['product_id'] = 'Product ID is required'
            if not amount: errors['amount'] = 'Amount is required'
            if not addr: errors['shipping_address'] = 'Shipping address is required'
            try:
                amount = float(amount); 
                if amount <= 0: errors['amount'] = 'Amount must be greater than 0'
            except: errors['amount'] = 'Invalid number'
            try: status = OrderStatus(request.form.get('status','').lower())
            except: errors['status'] = 'Invalid order status'
            if errors: return render_template('place_order.html', form_errors=errors)
            db.session.add(Order(user_id=current_user.id, product_id=product_id, product_name=product_name, amount=amount, status=status.value, shipping_address=addr, order_date=datetime.utcnow()))
            db.session.commit()
            flash('Order placed successfully!', 'success'); return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback(); current_app.logger.error(f'Order error: {e}', exc_info=True)
            flash('Order error. Try again.', 'danger')
    return render_template('place_order.html', form_errors=errors)

# --- Run ---
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with app.app_context(): db.create_all(); ensure_admin()
    app.run(debug=True, port=5000)