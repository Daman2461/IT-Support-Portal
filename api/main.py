from fastapi import FastAPI, Request
from pydantic import BaseModel
from agents.agent import agent_act

app = FastAPI()

class SupportRequest(BaseModel):
    user_input: str
    user_id: int

@app.post("/support/resolve")
def resolve_support(req: SupportRequest):
    """
    Resolve a customer support issue using the LLM-powered agent.

    - **user_input**: The customer's message (natural language)
    - **user_id**: The user's unique identifier

    Returns:
        - intent: The classified intent (refund, escalate, etc.)
        - action_result: The result of the backend action (JSON)

    Example request:
        {
            "user_input": "I want a refund for my damaged item",
            "user_id": 1
        }
    Example response:
        {
            "intent": "refund",
            "action_result": {"success": true, ...}
        }
    """
    result = agent_act(req.user_input, req.user_id)
    return result

# Optionally, add a health check
@app.get("/health")
def health():
    """Health check endpoint. Returns status ok if the service is running."""
    return {"status": "ok"}
