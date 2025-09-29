from datetime import datetime, timedelta
from db.schema import SessionLocal, Order, OrderStatus, db
from audit.logger import log_action

def trigger_replacement(order_id: int, reason: str = "Defective product"):
    """
    Initiate a replacement for an existing order.
    
    Args:
        order_id: ID of the order to be replaced
        reason: Reason for replacement (default: "Defective product")
        
    Returns:
        dict: Result of the replacement operation
    """
    session = SessionLocal()
    try:
        # Get the original order
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            result = {"success": False, "error": "Order not found"}
            log_action("replacement_failed", {"order_id": order_id, "reason": "Order not found"}, result)
            return result

        # Check if order status allows replacement
        if order.status != OrderStatus.SHIPPED.value:
            result = {
                "success": False,
                "error": f"Order status '{order.status}' is not eligible for replacement"
            }
            log_action("replacement_failed", {"order_id": order_id, "status": order.status}, result)
            return result

        # Check 15-day replacement window
        if datetime.utcnow() > order.order_date + timedelta(days=15):
            result = {
                "success": False,
                "error": "Replacement window has expired (15 days from order date)"
            }
            log_action("replacement_failed", {"order_id": order_id, "order_date": order.order_date.isoformat()}, result)
            return result

        # Check if user had another replacement in the last 15 days
        fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
        recent_replacements = (
            session.query(Order)
            .filter(
                Order.user_id == order.user_id,
                Order.status == OrderStatus.SHIPPED.value,  # only shipped orders count
                Order.order_date >= fifteen_days_ago
            )
            .count()
        )
        if recent_replacements > 0:
            result = {
                "success": False,
                "error": "You cannot request another replacement within 15 days of a previous replacement"
            }
            log_action("replacement_failed", {"order_id": order_id, "user_id": order.user_id}, result)
            return result

        # Create a replacement order
        replacement_order = Order(
            user_id=order.user_id,
            product_id=order.product_id,
            product_name=order.product_name,
            amount=0.00,  # Replacement is free
            shipping_address=order.shipping_address,
            status=OrderStatus.PENDING.value,  # replacement starts as pending
            order_date=datetime.utcnow()
        )

        # Update original order status
        order.status = OrderStatus.SHIPPED.value  # original order remains shipped

        # Commit changes
        session.add(replacement_order)
        session.commit()

        response_message = (
            f"I've initiated a replacement for your order #{order.id} "
            f"({order.product_name or 'product'}). "
            f"Your replacement order #{replacement_order.id} has been created and is now pending processing. "
            "You'll receive a confirmation email with tracking information shortly."
        )

        result = {
            "success": True,
            "original_order_id": order.id,
            "replacement_order_id": replacement_order.id,
            "status": "Replacement initiated",
            "response": response_message,
            "details": {
                "product_name": order.product_name,
                "original_status": order.status,
                "replacement_status": replacement_order.status,
                "replacement_date": replacement_order.order_date.isoformat(),
                "reason": reason
            }
        }

        log_action("replacement_triggered", {"order_id": order_id, "replacement_id": replacement_order.id}, result)
        return result

    except Exception as e:
        session.rollback()
        result = {
            "success": False,
            "error": f"Error processing replacement: {str(e)}"
        }
        log_action("replacement_error", {"order_id": order_id, "error": str(e)}, result)
        return result

    finally:
        session.close()