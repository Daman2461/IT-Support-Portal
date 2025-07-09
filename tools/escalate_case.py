from audit.logger import log_action

def escalate_case(order_id: int, user_id: int):
    # Simulate escalation (could add to a queue, etc.)
    result = {"success": True, "order_id": order_id, "user_id": user_id, "escalated": True}
    log_action("escalate_case", {"order_id": order_id, "user_id": user_id}, result)
    return result
