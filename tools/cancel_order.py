from db.schema import SessionLocal, Order, OrderStatus
from audit.logger import log_action

def cancel_order(order_id: int):
    session = SessionLocal()
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        result = {"success": False, "error": "Order not found"}
    elif order.status == OrderStatus.CANCELLED:
        result = {"success": False, "error": "Order already cancelled"}
    else:
        order.status = OrderStatus.CANCELLED
        session.commit()
        result = {"success": True, "order_id": order.id, "status": order.status.value}
    log_action("cancel_order", {"order_id": order_id}, result)
    session.close()
    return result
