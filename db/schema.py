from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import enum
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

# Database URL configuration
import os

# Use a single database file in the project root
DATABASE_URL = 'sqlite:////Users/daman/Support Agent/support_agent.db'
print(f"Using database at: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session factory
db_session = scoped_session(SessionLocal)

# Base class for models
Base = db.Model

# Initialize db with the app
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Create default admin user if it doesn't exist
        admin = db_session.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db_session.add(admin)
            db_session.commit()

# Enums (using Python's native enum)
class OrderStatus(enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

class TicketStatus(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'

class TicketPriority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

# Association Tables (if needed)
# user_roles = db.Table('user_roles',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#     db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
# )

# Models
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    tickets = db.relationship('Ticket', back_populates='user')
    orders = db.relationship('Order', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Order(db.Model):
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value, 
                      info={'choices': [e.value for e in OrderStatus]})
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='orders')
    refunds = db.relationship('RefundHistory', back_populates='order')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status.value}>'

class RefundHistory(db.Model):
    __tablename__ = 'refund_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    refund_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    is_fraudulent = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User')
    order = db.relationship('Order', back_populates='refunds')
    
    def __repr__(self):
        return f'<Refund {self.id} - ${self.amount}>'

class Ticket(db.Model):
    __tablename__ = 'ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=TicketStatus.OPEN.value,
                      info={'choices': [e.value for e in TicketStatus]})
    priority = db.Column(db.String(20), default=TicketPriority.MEDIUM.value,
                        info={'choices': [e.value for e in TicketPriority]})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    llm_intent = db.Column(db.String(50))
    llm_action_result = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', back_populates='tickets')
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.title}>'

def init_db():
    """Initialize the database with required tables and default data."""
    # Create all tables
    db.create_all()
    
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Created default admin user')

# This allows other modules to import models directly from db.models
# Example: from db.models import User, Order, etc.
__all__ = ['db', 'User', 'Order', 'Ticket', 'RefundHistory', 
           'OrderStatus', 'TicketStatus', 'TicketPriority', 'init_db'] 