from db.schema import SessionLocal, RefundHistory, Order, User
from audit.logger import log_action
from datetime import datetime, timedelta

def issue_refund(order_id: int, user_id: int, amount: float, reason: str):
    session = SessionLocal()
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    refund_count = session.query(RefundHistory).filter(
        RefundHistory.user_id == user_id,
        RefundHistory.refund_date >= month_ago
    ).count()
    if refund_count >= 2:
        result = {"success": False, "error": "Refund limit exceeded for user"}
    else:
        refund = RefundHistory(
            user_id=user_id,
            order_id=order_id,
            refund_date=now,
            amount=amount,
            reason=reason,
            is_fraudulent=False
        )
        session.add(refund)
        session.commit()
        result = {"success": True, "refund_id": refund.id, "order_id": order_id, "user_id": user_id, "amount": amount, "reason": reason}
    log_action("issue_refund", {"order_id": order_id, "user_id": user_id, "amount": amount, "reason": reason}, result)
    session.close()
    return result
