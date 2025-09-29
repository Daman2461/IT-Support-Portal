from typing import Optional
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
 

# --- Assume these functions are imported from your other files ---
from tools.cancel_order import cancel_order
from tools.issue_refund import issue_refund
from tools.escalate_case import escalate_case
from tools.get_order_status import get_order_status
from tools.trigger_replacement import trigger_replacement
from tools.place_order import place_order
from tools.tavily_search import search_web
from tools.find_orders import find_orders_by_user
def format_orders_as_table(orders: List[Dict[str, Any]]) -> str:
    """
    Formats a list of order dictionaries into a series of plain-text paragraphs.
    """
    if not orders:
        return "No orders were found."
    output_paragraphs = ["Here are your orders:\n"]
    for order in orders:
        order_id = order.get('id', 'N/A')
        product = order.get('product', 'Unknown Product')
        amount = f"${order.get('amount', 0.0):,.2f}"
        status = order.get('status', 'N/A')
        date = str(order.get('date', 'N/A')).split(' ')[0]
        paragraph = (
            f"Order #{order_id} is for {product} with a total of {amount}. "
            f"It was placed on {date} and the current status is {status}."
        )
        output_paragraphs.append(paragraph)
    final_instruction = "\n\nPlease present this full list to the user and then ask what they would like to do next."
    output_paragraphs.append(final_instruction)
    return "\n\n".join(output_paragraphs)

# -------------------------------------------------------------

# Define Pydantic models for the arguments of each tool.
# This provides a clear schema for the AI to follow.

class FindOrdersInput(BaseModel):
    """Input for the find_orders_by_user tool."""
    user_id: int = Field(description="The unique identifier for the user.")
    product_name: Optional[str] = Field(None, description="Optional: The name of a product to filter orders by.")

class OrderIdInput(BaseModel):
    """Input for any tool that requires a single order_id."""
    order_id: int = Field(description="The unique identifier for the order.")

class CancelOrderInput(BaseModel):
    """Input for the cancel_order tool."""
    order_id: int = Field(description="The ID of the order to be cancelled.")
    user_id: int = Field(description="The ID of the user who owns the order.")

class IssueRefundInput(BaseModel):
    """Input for the issue_refund tool."""
    order_id: int = Field(description="The ID of the order to be refunded.")
    user_id: int = Field(description="The ID of the user who owns the order.")
    amount: float = Field(description="The amount to be refunded.")
    reason: str = Field(description="The reason for issuing the refund.")

class PlaceOrderInput(BaseModel):
    product_name: str = Field(description="The full name of the product.")
    product_id: str = Field(description="The unique ID of the product.")
    amount: float = Field(description="The final price of the product.")
    shipping_address: str = Field(description="The complete shipping address.")
    user_id: int = Field(description="The ID of the user placing the order.")


class EscalateCaseInput(BaseModel):
    """Input for the escalate_case tool."""
    order_id: int = Field(description="The order ID related to the issue. Use 0 if not tied to a specific order.")
    user_id: int = Field(description="The ID of the user whose case is being escalated.")

class TriggerReplacementInput(BaseModel):
    """Input for the trigger_replacement tool."""
    order_id: int = Field(description="The ID of the order that needs a replacement.")
    reason: str = Field("Defective product", description="The reason for the replacement.")


def find_orders_wrapper(user_id: int, product_name: Optional[str] = None) -> str:
    raw_orders_result = find_orders_by_user(user_id=user_id, product_name=product_name)
    if raw_orders_result.get("success") and raw_orders_result.get("orders"):
        return format_orders_as_table(raw_orders_result["orders"]) # This now calls the function in this same file
    elif not raw_orders_result.get("orders"):
        return "No orders were found for this user."
    else:
        return f"An error occurred: {raw_orders_result.get('error', 'Unknown error')}"


# Note: We now pass the original functions directly.
# LangChain and Pydantic handle all the parsing and validation.
find_orders_tool = StructuredTool.from_function(
    func=find_orders_wrapper,
    name="find_orders_by_user",
    description="Find all orders for a user. Returns a formatted list.",
    args_schema=FindOrdersInput
)

get_order_status_tool = StructuredTool.from_function(
    func=get_order_status,
    name="get_order_status",
    description="Get the current status of a specific order using its ID.",
    args_schema=OrderIdInput
)

cancel_order_tool = StructuredTool.from_function(
    func=cancel_order,
    name="cancel_order",
    description="Cancel a customer's order.",
    args_schema=CancelOrderInput
)

issue_refund_tool = StructuredTool.from_function(
    func=issue_refund,
    name="issue_refund",
    description="Issue a refund for a specific order.",
    args_schema=IssueRefundInput
)

place_order_tool = StructuredTool.from_function(
    func=place_order,
    name="place_order",
    description=(
        "Use this tool to finalize and place a new order for a user. "
        "You MUST have the user's confirmation and all of the following details before using this tool: "
        "product_name, product_id, amount, and shipping_address. "
        "If any of this information is missing, you MUST ask the user for it."
    ),
    args_schema=PlaceOrderInput
)

escalate_case_tool = StructuredTool.from_function(
    func=escalate_case,
    name="escalate_case",
    description="Escalate an issue to a human agent when a problem cannot be solved.",
    args_schema=EscalateCaseInput
)

# A simple tool like a web search doesn't need a structured schema,
# as it just takes a single string. The basic Tool class is fine here.
search_web_tool = Tool(
    name="search_web",
    description="Search the web for current information or information outside of the order system.",
    func=search_web
)
trigger_replacement_tool = StructuredTool.from_function(
    func=trigger_replacement, # Make sure 'trigger_replacement' is imported
    name="trigger_replacement",
    description="Initiate a replacement for an item in an order.",
    args_schema=TriggerReplacementInput
)

# List of all tools for easy registration in your agent
all_tools = [
    find_orders_tool,
    get_order_status_tool,
    cancel_order_tool,
    issue_refund_tool,
    place_order_tool,
    escalate_case_tool,
    search_web_tool,
    # The 'trigger_replacement' tool was in your original code. If you still need it,
    # you would create it the same way as the others:
     trigger_replacement_tool,
]