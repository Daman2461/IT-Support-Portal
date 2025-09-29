from db.schema import SessionLocal, RefundHistory, Order, User, OrderStatus
from audit.logger import log_action
from datetime import datetime, timedelta

def issue_refund(order_id: int, user_id: int, amount: float, reason: str):
    result = {"success": False, "error": "An unknown error occurred"}
    session = SessionLocal()
    try:
        # Check if order exists and belongs to user
        order = session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()
        
        if not order:
            return {"success": False, "error": "Order not found or does not belong to user"}
            
        # Only allow refunds for cancelled orders or perishable goods
        if order.status != OrderStatus.CANCELLED.value:
            # Check if product is perishable by searching the web
            from tools.tavily_search import search_web
            search_results = search_web(f"Is {order.product_name} a perishable good?")
            is_perishable = any(word in str(search_results).lower() for word in ["perishable", "spoil", "expire", "shelf life"])
            
            if not is_perishable:
                return {"success": False, "error": "Refunds are only allowed for cancelled orders or perishable goods"}
        
        # Check refund limit (max 2 refunds per month)
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        refund_count = session.query(RefundHistory).filter(
            RefundHistory.user_id == user_id,
            RefundHistory.refund_date >= month_ago
        ).count()
        
        if refund_count >= 2:
            return {
                "success": False, 
                "error": "Refund limit exceeded. Maximum 2 refunds allowed per month."
            }
            
        # Check if refund amount is valid
        if amount <= 0 or amount > order.amount:
            return {
                "success": False,
                "error": f"Invalid refund amount. Must be between 0 and {order.amount}"
            }
            
        # Create refund record
        refund = RefundHistory(
            user_id=user_id,
            order_id=order_id,
            refund_date=now,
            amount=amount,
            reason=reason,
            is_fraudulent=False
        )
        
        session.add(refund)
        
        # Update order status if full refund
        if amount == order.amount:
            order.status = OrderStatus.CANCELLED.value
        
        session.commit()
        
        result = {
            "success": True, 
            "refund_id": refund.id, 
            "order_id": order_id, 
            "user_id": user_id, 
            "amount": amount, 
            "reason": reason,
            "message": f"Refund of ${amount:.2f} processed successfully"
        }
        
    except Exception as e:
        session.rollback()
        result = {
            "success": False, 
            "error": f"Error processing refund: {str(e)}"
        }
        
    finally:
        log_action("issue_refund", {
            "order_id": order_id, 
            "user_id": user_id, 
            "amount": amount, 
            "reason": reason
        }, result)
        session.close()
        
    return result
