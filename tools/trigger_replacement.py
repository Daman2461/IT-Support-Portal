from db.schema import SessionLocal, Order
from audit.logger import log_action

def trigger_replacement(order_id: int):
    session = SessionLocal()
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        result = {"success": False, "error": "Order not found"}
    else:
        # Simulate replacement logic (could add a field or just log)
        result = {"success": True, "order_id": order.id, "replacement_triggered": True}
    log_action("trigger_replacement", {"order_id": order_id}, result)
    session.close()
    return result
