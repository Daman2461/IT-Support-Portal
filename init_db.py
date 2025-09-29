import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.schema import Base, User, Order, Ticket, RefundHistory, OrderStatus, TicketStatus, TicketPriority
from werkzeug.security import generate_password_hash

# Use the same database URL as the frontend
DATABASE_URL = 'sqlite:////Users/daman/Support Agent/support_agent.db'
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    # Create default admin user if it doesn't exist
    if not db.query(User).filter_by(username='admin').first():
        admin = User(
            username='admin',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.add(admin)
        db.commit()
        print('Created default admin user')
    
    db.close()

if __name__ == '__main__':
    print('Initializing database...')
    init_db()
    print('Database initialized successfully!')
