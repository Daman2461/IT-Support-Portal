from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import urlencode

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///support_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='user')
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tickets = db.relationship('Ticket', backref='user', lazy=True)
    articles = db.relationship('Article', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='ticket', lazy=True)
    llm_intent = db.Column(db.String(50))
    llm_action_result = db.Column(db.Text)

    @property
    def status_color(self):
        colors = {
            'open': 'primary',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'secondary'
        }
        return colors.get(self.status, 'secondary')

    @property
    def priority_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        }
        return colors.get(self.priority, 'secondary')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    articles = db.relationship('Article', backref='category', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            department=department,
            phone=phone
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/')
@login_required
def dashboard():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    open_tickets_count = Ticket.query.filter_by(user_id=current_user.id, status='open').count()
    resolved_tickets_count = Ticket.query.filter_by(user_id=current_user.id, status='resolved').count()
    in_progress_tickets_count = Ticket.query.filter_by(user_id=current_user.id, status='in_progress').count()
    total_tickets_count = Ticket.query.filter_by(user_id=current_user.id).count()
    
    popular_articles = Article.query.order_by(Article.views.desc()).limit(3).all()
    
    return render_template('dashboard.html',
                         tickets=tickets,
                         open_tickets_count=open_tickets_count,
                         resolved_tickets_count=resolved_tickets_count,
                         in_progress_tickets_count=in_progress_tickets_count,
                         total_tickets_count=total_tickets_count,
                         popular_articles=popular_articles)

@app.route('/ticket/<int:ticket_id>/llm-result', methods=['GET', 'POST'])
@login_required
def ticket_llm_result(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    agent_result = None
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'satisfied':
            # Mark ticket as resolved
            ticket.status = 'resolved'
            db.session.commit()
            flash('Thank you for your feedback! Ticket marked as resolved.', 'success')
            return redirect(url_for('my_tickets'))
        elif choice == 'escalate':
            # Send email notification for escalation
            try:
                msg = Message(
                    'Support Ticket Escalation Request',
                    recipients=[current_user.email]
                )
                msg.body = f'''
                Your support ticket has been escalated to a human agent.
                
                Ticket Details:
                - Ticket ID: {ticket.id}
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Priority: {ticket.priority}
                
                A human agent will contact you within 24 hours.
                '''
                mail.send(msg)
                flash('Your request has been escalated. A human agent will contact you via email.', 'info')
            except Exception as e:
                flash('Escalation request received. A human agent will contact you soon.', 'info')
            return redirect(url_for('my_tickets'))
    # Retrieve LLM result from flash or session (for demo, use flash messages)
    agent_result = request.args.get('agent_result')
    return render_template('ticket_llm_result.html', ticket=ticket, agent_result=agent_result)

@app.route('/ticket/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        ticket = Ticket(
            title=request.form['title'],
            description=request.form['description'],
            priority=request.form['priority'],
            user_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()

        # Send to FastAPI agent
        import requests
        agent_result = None
        try:
            response = requests.post(
                'http://127.0.0.1:8000/support/resolve',
                json={'user_input': f"{ticket.title}: {ticket.description}", 'user_id': ticket.user_id},
                timeout=30
            )
            if response.status_code == 200:
                agent_result = response.json()
                # Store LLM result in ticket
                ticket.llm_intent = agent_result.get('intent')
                ticket.llm_action_result = str(agent_result.get('action_result'))
                db.session.commit()
            else:
                agent_result = {'error': f'Agent API error: {response.status_code}'}
        except Exception as e:
            agent_result = {'error': str(e)}

        # Pass agent_result to llm-result page (as query param for demo)
        from urllib.parse import urlencode
        params = urlencode({'agent_result': str(agent_result)})
        return redirect(url_for('ticket_llm_result', ticket_id=ticket.id) + f'?{params}')
    return render_template('new_ticket.html')

@app.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    # Provide related_articles to the template (e.g., 3 most recent articles)
    related_articles = Article.query.order_by(Article.created_at.desc()).limit(3).all()
    return render_template('view_ticket.html', ticket=ticket, related_articles=related_articles)

@app.route('/ticket/<int:ticket_id>/update-status', methods=['POST'], endpoint='update_ticket_status')
@login_required
def update_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get('status')
    if new_status:
        ticket.status = new_status
        db.session.commit()
        flash('Ticket status updated.', 'success')
    else:
        flash('No status provided.', 'warning')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    comment = Comment(
        content=request.form['content'],
        user_id=current_user.id,
        ticket_id=ticket_id
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'content': comment.content,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'username': current_user.username
    })

@app.route('/my-tickets')
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('my_tickets.html', tickets=tickets)

@app.route('/knowledge-base')
@login_required
def knowledge_base():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search', '')
    
    query = Article.query
    
    if category:
        query = query.filter_by(category_id=category)
    if search:
        query = query.filter(Article.title.ilike(f'%{search}%') | Article.content.ilike(f'%{search}%'))
    
    pagination = query.order_by(Article.updated_at.desc()).paginate(page=page, per_page=10)
    categories = Category.query.all()
    
    return render_template('knowledge_base.html',
                         articles=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         category=category)

@app.route('/knowledge-base/article/<int:article_id>')
@login_required
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.views += 1
    db.session.commit()
    
    related_articles = Article.query.filter_by(category_id=article.category_id)\
        .filter(Article.id != article_id)\
        .order_by(Article.views.desc())\
        .limit(3).all()
    
    return render_template('view_article.html',
                         article=article,
                         related_articles=related_articles)

@app.route('/knowledge-base/article/<int:article_id>/feedback', methods=['POST'])
@login_required
def article_feedback(article_id):
    article = Article.query.get_or_404(article_id)
    feedback = request.form.get('feedback')
    
    if feedback == 'helpful':
        article.helpful_count += 1
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
    else:
        flash('Thank you for your feedback. We\'ll work to improve this article.', 'info')
    
    return redirect(url_for('view_article', article_id=article_id))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile update
        if 'update_profile' in request.form:
            current_user.username = request.form.get('username')
            current_user.email = request.form.get('email')
            current_user.department = request.form.get('department')
            current_user.phone = request.form.get('phone')
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        # Handle password change
        elif 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
    
    # Get user statistics
    total_tickets = Ticket.query.filter_by(user_id=current_user.id).count()
    resolved_tickets = Ticket.query.filter_by(user_id=current_user.id, status='resolved').count()
    open_tickets = Ticket.query.filter_by(user_id=current_user.id, status='open').count()
    
    return render_template('profile.html',
                         total_tickets=total_tickets,
                         resolved_tickets=resolved_tickets,
                         open_tickets=open_tickets)

@app.route('/ai-support', methods=['GET', 'POST'])
@login_required
def ai_support():
    result = None
    if request.method == 'POST':
        user_input = request.form['message']
        user_id = current_user.id
        try:
            response = requests.post(
                'http://127.0.0.1:8000/support/resolve',
                json={'user_input': user_input, 'user_id': user_id},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
            else:
                result = {'error': f'API error: {response.status_code}'}
        except Exception as e:
            result = {'error': str(e)}
    return render_template('ai_support.html', result=result)

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create a default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                department='IT',
                phone='123-456-7890'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Created default admin user')
    
    app.run(debug=True) 