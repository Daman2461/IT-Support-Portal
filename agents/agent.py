import os
import logging
from dotenv import load_dotenv

# --- Setup (assumed to be the same) ---
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from tools.langchain_tools import all_tools # Assuming your tools are correctly defined here

# --- LLM and Memory Setup (Corrected) ---
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    api_key=api_key,
    model_name="gpt-3.5-turbo",
    temperature=0.1
)

# Set up memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- Agent Initialization (Corrected) ---

# Your detailed instructions should be a system message for the agent
# This is the correct way to provide context and rules.
system_message_content = f"""
You are a helpful customer support AI. Follow these instructions carefully.



Examples of phrases that require immediate escalation:
- 'not happy', 'unhappy', 'dissatisfied', 'upset', 'angry', 'frustrated'
- 'bad experience', 'poor service', 'terrible service'
- 'speak to human', 'talk to agent', 'manager', 'supervisor'
- 'escalate', 'not good enough', 'not acceptable'
[OUTPUT HANDLING]
- When a tool returns a string that starts with '<', you MUST assume it is pre-formatted HTML.
- Your final answer in this case MUST be ONLY the exact string returned by the tool, with no additional text, summarization, or re-formatting.

[TOOL USAGE RULES]
- You MUST NOT confirm that an action (like cancelling an order, issuing a refund, or placing an order) has been completed unless you have first used the corresponding tool and it has returned a success message.
- If the user asks to perform an action but does not provide all the necessary information (e.g., asking to cancel an order without an order_id), you MUST ask for the missing information. Do not guess.


 
[General Guidelines]
1. ALWAYS use the appropriate tool for the user's request.
2. NEVER make up information; use tools to get real data.
3. When showing order details from `find_orders_by_user`, display ALL available information without summarizing.
"""

# Use agent_kwargs to pass the system message and memory variables correctly
agent_kwargs = {
    "system_message": SystemMessage(content=system_message_content),
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
}
react_prompt ="""You are an intelligent agent capable of reasoning and interacting with tools to solve problems.

**Instructions:**
1.  **Thought:** Always explain your reasoning and plan before taking an action.
2.  **Action:** Use the available tools to gather information or perform tasks.
    *   Available Tools:
        *   `search(query: str)`: Searches the internet for information.
        *   `calculate(expression: str)`: Evaluates a mathematical expression.
3.  **Observation:** Report the outcome of your action.
4.  Repeat this process until you have a complete answer.

**Task:** {user_query}

**Example Interaction:**

**Thought:** I need to find the capital of France.
**Action:** search("capital of France")
**Observation:** The capital of France is Paris.
**Thought:** I have found the answer.
**Action:** Respond("The capital of France is Paris.")
**Observation:** Response sent.

---

**Current Interaction:**"""
agent: AgentExecutor = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True, 
    handle_parsing_errors=True,
    memory=memory,
    agent_kwargs=agent_kwargs,
    max_iterations=5,
    early_stopping_method="generate"
)

# --- Agent Invocation Function (Corrected and Simplified) ---

def agent_act(user_input: str, user_id: int = None):
    """
    Invokes the ReAct agent with the user's input.
    The agent will handle memory and prompt construction internally.
    """
    try:
        if not user_input or not isinstance(user_input, str):
            raise ValueError("Invalid user input")
 
        contextual_input = f"User Input: '{user_input}'. (Context: user_id is {user_id})"

        # Use .invoke() which is the standard method now
        result = agent.invoke({"input": contextual_input})

        # The output from .invoke() is a dictionary, the answer is in the 'output' key
        final_answer = result.get('output', "I'm sorry, I couldn't process that.")

        return {
            "response": final_answer,
            "success": True
        }

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return {
            "response": "I'm sorry, something went wrong. Please try your request again.",
            "success": False,
            "error": error_msg
        }


if __name__ == '__main__':
    print("Agent is ready. Type 'exit' to quit.")
    current_user_id = 2 # Example user_id

    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        
        response = agent_act(user_query, user_id=current_user_id)
        print(f"Agent: {response['response']}")
