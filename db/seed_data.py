from db.schema import Base, engine, SessionLocal, User, Product, Order, RefundHistory, OrderStatus, init_db
from faker import Faker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import random
from datetime import datetime, timedelta

def seed():
    fake = Faker()
    session = SessionLocal()
    # Only seed if tables are empty
    if session.query(User).count() > 0:
        print("DB already seeded.")
        session.close()
        return

    # Users
    users = [User(name=fake.name(), email=fake.unique.email()) for _ in range(5)]
    session.add_all(users)
    session.commit()

    # Products
    products = [Product(name=fake.word().capitalize(), price=round(random.uniform(10, 200), 2), sku=fake.unique.ean(length=8), stock=random.randint(10, 100)) for _ in range(5)]
    session.add_all(products)
    session.commit()

    # Orders
    orders = []
    for _ in range(10):
        user = random.choice(users)
        product = random.choice(products)
        status = random.choice(list(OrderStatus))
        order = Order(
            user_id=user.id,
            product_id=product.id,
            status=status,
            order_date=fake.date_time_between(start_date='-2M', end_date='now'),
            amount=product.price
        )
        orders.append(order)
    session.add_all(orders)
    session.commit()

    # Refunds (some random orders)
    for order in random.sample(orders, 3):
        refund = RefundHistory(
            user_id=order.user_id,
            order_id=order.id,
            refund_date=order.order_date + timedelta(days=random.randint(1, 10)),
            amount=order.amount,
            reason=random.choice(["damaged item", "late delivery", "wrong item"]),
            is_fraudulent=False
        )
        session.add(refund)
    session.commit()
    session.close()
    print("DB seeded.")

if __name__ == "__main__":
    init_db()
    seed()
