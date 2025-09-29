# tests/test_workflow.py
import pytest
from agents.agent import agent_act
from unittest.mock import patch, MagicMock, ANY
from langchain.agents import AgentExecutor

@pytest.fixture
def mock_agent():
    # Create a mock for the agent
    mock_agent = MagicMock(spec=AgentExecutor)
    
    # Set up the mock return values
    def invoke_side_effect(input_data, **kwargs):
        user_input = input_data.get('input', '')
        if 'refund' in user_input.lower():
            return {'output': 'Your refund has been processed.'}
        elif 'escalat' in user_input.lower():
            return {'output': 'Your case has been escalated.'}
        elif 'status' in user_input.lower():
            return {'output': 'Your order status is shipped.'}
        elif 'replacement' in user_input.lower():
            return {'output': 'Your replacement has been initiated.'}
        return {'output': "I'm not sure how to help with that."}
    
    mock_agent.invoke.side_effect = invoke_side_effect
    return mock_agent

def test_successful_refund(mock_agent):
    """Test that refund requests are handled correctly."""
    with patch('agents.agent.agent', mock_agent):
        response = agent_act("I want to refund order 123", user_id=1)
        assert "refund" in response["response"].lower()
        mock_agent.invoke.assert_called_once()

def test_escalation(mock_agent):
    """Test that escalation requests are handled correctly."""
    with patch('agents.agent.agent', mock_agent):
        response = agent_act("I need to speak to a manager", user_id=1)
        assert "escalat" in response["response"].lower()
        mock_agent.invoke.assert_called_once()

def test_status_inquiry(mock_agent):
    """Test that status inquiries are handled correctly."""
    with patch('agents.agent.agent', mock_agent):
        response = agent_act("What's the status of order 123?", user_id=1)
        assert "status" in response["response"].lower()
        mock_agent.invoke.assert_called_once()

def test_replacement_request(mock_agent):
    """Test that replacement requests are handled correctly."""
    with patch('agents.agent.agent', mock_agent):
        response = agent_act("I need a replacement for order 123", user_id=1)
        assert "replacement" in response["response"].lower()
        mock_agent.invoke.assert_called_once()
