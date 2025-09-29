from db.schema import SessionLocal, Order
from audit.logger import log_action

def get_order_status(order_id: int):
    session = SessionLocal()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            result = {"success": False, "error": "Order not found"}
        else:
            result = {
                "success": True,
                "order_id": order.id,
                "status": order.status,  # No need for .value since we're using strings now
                "user_id": order.user_id,
                "product_id": order.product_id,
                "product_name": order.product_name,
                "amount": order.amount,
                "order_date": str(order.order_date),
                "shipping_address": order.shipping_address
            }
    except Exception as e:
        result = {"success": False, "error": f"Error fetching order: {str(e)}"}
    log_action("get_order_status", {"order_id": order_id}, result)
    session.close()
    return result
