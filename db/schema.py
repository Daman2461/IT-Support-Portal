from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, create_engine, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship('Order', back_populates='user')
    refunds = relationship('RefundHistory', back_populates='user')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    stock = Column(Integer, default=0)
    orders = relationship('Order', back_populates='product')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    order_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    user = relationship('User', back_populates='orders')
    product = relationship('Product', back_populates='orders')
    refund = relationship('RefundHistory', back_populates='order', uselist=False)

class RefundHistory(Base):
    __tablename__ = 'refund_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    refund_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    reason = Column(String)
    is_fraudulent = Column(Boolean, default=False)
    user = relationship('User', back_populates='refunds')
    order = relationship('Order', back_populates='refund')

# SQLite engine and session
engine = create_engine('sqlite:///supportopsagent.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
