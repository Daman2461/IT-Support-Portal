from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from agents.agent import agent_act
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

from typing import Union

class SupportRequest(BaseModel):
    user_input: str
    user_id: Union[int, str]  # Accept both int and string user IDs
    conversation_id: Optional[str] = None
    conversation_history: List[Dict] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            # Ensure user_id is always serialized as string
            int: lambda v: str(v),
        }

class SupportResponse(BaseModel):
    response: str
    conversation_id: str
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = {}

# In-memory conversation store (replace with Redis in production)
conversation_store = {}

def get_conversation(conversation_id: str) -> List[Dict]:
    """Get conversation history from store."""
    return conversation_store.get(conversation_id, [])

def save_conversation(conversation_id: str, messages: List[Dict]):
    """Save conversation to store."""
    conversation_store[conversation_id] = messages

@app.post("/support/resolve", response_model=SupportResponse)
async def resolve_support(request: Request, req: SupportRequest):
    """
    Resolve a customer support issue using the LLM-powered agent.
    
    Request body should contain:
    - user_input: The customer's message
    - user_id: The user's ID (required, can be string or number)
    - conversation_id: (Optional) Existing conversation ID
    - conversation_history: (Optional) Previous messages in the conversation
    
    Returns:
    - response: The agent's response
    - conversation_id: The conversation ID
    - needs_clarification: Whether the agent needs more information
    - clarification_prompt: (If needed) Prompt to show the user
    - context: Additional context for the frontend
    """
    try:
        # Ensure user_id is provided and convert to string if it's a number
        if not hasattr(req, 'user_id') or req.user_id is None:
            raise HTTPException(status_code=400, detail="Missing required field: user_id")
            
        # Convert user_id to string if it's a number
        user_id = str(req.user_id)
        
        # Get or create conversation ID
        if not req.conversation_id or req.conversation_id not in conversation_store:
            req.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            conversation_history = []
        else:
            conversation_history = get_conversation(req.conversation_id)
        
        # Add user message to conversation history
        user_message = {
            "role": "user",
            "content": req.user_input,
            "timestamp": None,  # Will be set by the frontend
            "metadata": {}
        }
        conversation_history.append(user_message)
        
        # Call the agent
        try:
            logger.info(f"Calling agent with user_id: {user_id} (type: {type(user_id)})")
            agent_response = agent_act(
                user_input=req.user_input,
                user_id=user_id  # Now properly formatted as string
            )
            
            # Log the response for debugging
            logger.info(f"Agent response: {agent_response}")
            
            # Ensure we have a valid response
            if not agent_response or not isinstance(agent_response, dict):
                raise ValueError("Invalid response from agent")
                
            # Check if the agent reported an error
            if not agent_response.get('success', True):
                logger.error(f"Agent reported error: {agent_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Error calling agent_act: {str(e)}"
            logger.error(error_msg)
            agent_response = {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "success": False,
                "error": error_msg,
                "needs_clarification": False,
                "metadata": {"error": error_msg}
            }
        
        # Add assistant response to conversation history
        assistant_message = {
            "role": "assistant",
            "content": agent_response.get('response', 'I apologize, but I encountered an error.'),
            "timestamp": None,  # Will be set by the frontend
            "metadata": {
                "needs_clarification": agent_response.get('needs_clarification', False),
                "success": agent_response.get('success', False),
                **agent_response.get('metadata', {})
            }
        }
        conversation_history.append(assistant_message)
        
        # Save updated conversation
        save_conversation(req.conversation_id, conversation_history)
        
        # Prepare the response data
        response_data = {
            "response": agent_response.get('response', 'I apologize, but I encountered an error.'),
            "success": agent_response.get('success', True),
            "conversation_id": req.conversation_id,
            "needs_clarification": agent_response.get('needs_clarification', False),
            "metadata": {
                **agent_response.get('metadata', {})
            }
        }
        
        # Add details if they exist
        if 'details' in agent_response:
            response_data['details'] = agent_response['details']
            
        # Add error if it exists
        if 'error' in agent_response:
            response_data['error'] = agent_response['error']
        
        # Return the response
        return response_data
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        return {
            "response": "I'm sorry, but I encountered an error processing your request. Please try again later.",
            "conversation_id": req.conversation_id if 'req' in locals() else "",
            "needs_clarification": False,
            "metadata": {"error": error_msg}
        }

@app.get("/conversation/{conversation_id}")
async def get_conversation_endpoint(conversation_id: str):
    """Get the full conversation history for a given conversation ID."""
    if conversation_id not in conversation_store:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation": conversation_store[conversation_id]}

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversation_store:
        del conversation_store[conversation_id]
    return {"status": "success"}

@app.get("/health")
async def health():
    """Health check endpoint. Returns status ok if the service is running."""
    return {"status": "ok"}


