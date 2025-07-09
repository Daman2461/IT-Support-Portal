import os
import re
from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai.chat_models import ChatMistralAI
from rag.policy_index import PolicyRetriever
from utils.redact import redact_pii
from tools.get_order_status import get_order_status
from tools.issue_refund import issue_refund
from tools.cancel_order import cancel_order
from tools.trigger_replacement import trigger_replacement
from tools.escalate_case import escalate_case

# Set up Mistral LLM via ChatMistralAI
api_key = os.getenv("MISTRAL_API_KEY")
llm = ChatMistralAI(api_key=api_key, model="mistral-medium")

# Policy retriever
policy_retriever = PolicyRetriever()

INTENT_KEYWORDS = ["refund", "cancel", "replacement", "escalate", "status", "other"]

def classify_intent(user_input: str, context_docs: str) -> str:
    prompt = f"""
    You are a support agent. Given the following user message and policy context, classify the intent as one of: refund, cancel, replacement, escalate, status, other. Only output the intent keyword.
    
    User: {user_input}
    Policy/FAQ: {context_docs}
    Intent:
    """
    response = llm.invoke(prompt).content.strip().lower()
    # Try to extract the intent keyword robustly
    for intent in INTENT_KEYWORDS:
        if re.search(rf"\b{intent}\b", response):
            return intent
    # fallback: first word
    return response.split()[0] if response.split() else "other"

def agent_act(user_input: str, user_id: int = None):
    # Step 1: Redact PII
    redacted_input = redact_pii(user_input)
    # Step 2: Retrieve policy context
    docs = policy_retriever.retrieve(redacted_input, k=2)
    context_docs = "\n".join([d.page_content for d in docs])
    # Step 3: Classify intent
    intent = classify_intent(redacted_input, context_docs)
    # Step 4: Route to tool
    # (In real use, would extract order_id, etc. via LLM or regex)
    # For demo, use dummy values or require explicit input
    if intent == "refund":
        # Dummy extraction for demo
        order_id = 1
        amount = 50.0
        reason = "damaged item"
        result = issue_refund(order_id, user_id, amount, reason)
    elif intent == "cancel":
        order_id = 1
        result = cancel_order(order_id)
    elif intent == "replacement":
        order_id = 1
        result = trigger_replacement(order_id)
    elif intent == "escalate":
        order_id = 1
        result = escalate_case(order_id, user_id)
    elif intent == "status":
        order_id = 1
        result = get_order_status(order_id)
    else:
        result = {"success": False, "error": "Intent not recognized or supported."}
    return {"intent": intent, "action_result": result}
