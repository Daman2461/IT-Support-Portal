from db.schema import SessionLocal, Order, OrderStatus
from audit.logger import log_action

def cancel_order(order_id: int, user_id: int):
    """
    Cancel an order by ID.
    
    Args:
        order_id: The order ID to cancel
        user_id: The ID of the user making the request
        
    Returns:
        Dictionary with result of the operation
    """
    session = SessionLocal()
    
    try:
        # Get the order
        order = session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()
        
        if not order:
            return {"success": False, "error": "Order not found or you don't have permission to cancel it"}
            
        if order.status == OrderStatus.CANCELLED.value:
            return {"success": False, "error": "This order has already been cancelled"}
            
        if order.status == OrderStatus.SHIPPED.value:
            return {"success": False, "error": "This order has already been shipped and cannot be cancelled"}
            
        # Update order status
        order.status = OrderStatus.CANCELLED.value
        session.commit()
        
        result = {
            "success": True, 
            "order_id": order.id,
            "product_name": order.product_name,
            "status": order.status,
            "message": f"Your order for '{order.product_name}' (Order #{order.id}) has been cancelled successfully."
        }
        
    except Exception as e:
        session.rollback()
        result = {
            "success": False, 
            "error": f"Error cancelling order: {str(e)}"
        }
    finally:
        log_action("cancel_order", {"order_id": order_id, "user_id": user_id}, result)
        session.close()
        return result
