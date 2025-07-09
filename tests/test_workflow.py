import pytest
from agents.agent import agent_act

def test_successful_refund(monkeypatch):
    def mock_issue_refund(order_id, user_id, amount, reason):
        return {"success": True, "refund_id": 1, "order_id": order_id, "user_id": user_id, "amount": amount, "reason": reason}
    monkeypatch.setattr("agents.agent.issue_refund", mock_issue_refund)
    result = agent_act("I want a refund for my damaged item", user_id=1)
    assert result["intent"] == "refund"
    assert result["action_result"]["success"]

def test_refund_limit(monkeypatch):
    def mock_issue_refund(order_id, user_id, amount, reason):
        return {"success": False, "error": "Refund limit exceeded for user"}
    monkeypatch.setattr("agents.agent.issue_refund", mock_issue_refund)
    result = agent_act("I want another refund", user_id=1)
    assert result["intent"] == "refund"
    assert not result["action_result"]["success"]
    assert "limit" in result["action_result"]["error"]

def test_escalation(monkeypatch):
    def mock_escalate_case(order_id, user_id):
        return {"success": True, "order_id": order_id, "user_id": user_id, "escalated": True}
    monkeypatch.setattr("agents.agent.escalate_case", mock_escalate_case)
    result = agent_act("I want to speak to a manager", user_id=1)
    assert result["intent"] == "escalate"
    assert result["action_result"]["escalated"]

def test_unknown_intent():
    result = agent_act("What is the weather today?", user_id=1)
    assert result["intent"] == "other"
    assert not result["action_result"]["success"]

def test_status_inquiry(monkeypatch):
    def mock_get_order_status(order_id):
        return {"success": True, "order_id": order_id, "status": "shipped"}
    monkeypatch.setattr("agents.agent.get_order_status", mock_get_order_status)
    result = agent_act("Where is my order?", user_id=1)
    assert result["intent"] == "status"
    assert result["action_result"]["success"]
    assert result["action_result"]["status"] == "shipped"

def test_replacement_request(monkeypatch):
    def mock_trigger_replacement(order_id):
        return {"success": True, "order_id": order_id, "replacement_triggered": True}
    monkeypatch.setattr("agents.agent.trigger_replacement", mock_trigger_replacement)
    result = agent_act("My item arrived broken, send a replacement", user_id=1)
    assert result["intent"] == "replacement"
    assert result["action_result"]["replacement_triggered"]

def test_fraud_detection(monkeypatch):
    # Simulate >2 refunds in a month
    def mock_issue_refund(order_id, user_id, amount, reason):
        return {"success": False, "error": "Refund limit exceeded for user", "is_fraudulent": True}
    monkeypatch.setattr("agents.agent.issue_refund", mock_issue_refund)
    result = agent_act("I want a refund again", user_id=1)
    assert result["intent"] == "refund"
    assert not result["action_result"]["success"]
    assert result["action_result"].get("is_fraudulent")

def test_pii_redaction(monkeypatch):
    # The agent should redact PII before LLM exposure
    def mock_classify_intent(user_input, context_docs):
        assert "john doe" not in user_input.lower()
        assert "john.doe@example.com" not in user_input.lower()
        return "refund"
    monkeypatch.setattr("agents.agent.classify_intent", mock_classify_intent)
    # The rest of the pipeline should work
    def mock_issue_refund(order_id, user_id, amount, reason):
        return {"success": True}
    monkeypatch.setattr("agents.agent.issue_refund", mock_issue_refund)
    result = agent_act("My name is John Doe, email john.doe@example.com, I want a refund", user_id=1)
    assert result["intent"] == "refund"
    assert result["action_result"]["success"]
