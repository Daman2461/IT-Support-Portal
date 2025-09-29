from typing import Dict, List, Optional, Tuple
from .find_order_by_product_name import find_orders_by_product_name, format_order_suggestion

def identify_order(user_id: int, user_message: str) -> Tuple[Optional[int], str]:
    """
    Identify an order ID from the user's message or search for matching orders.
    
    Args:
        user_id: ID of the user
        user_message: The user's message
        
    Returns:
        Tuple of (order_id, response_message)
        - If order ID is found or confirmed, returns (order_id, "")
        - If clarification is needed, returns (None, clarification_message)
        - If no matches found, returns (None, error_message)
    """
    # First, try to extract order ID directly from message
    import re
    order_id_match = re.search(r'(?:order|#)?\s*(\d{4,})', user_message)
    if order_id_match:
        return int(order_id_match.group(1)), ""
    
    # If no order ID found, search for product names
    search_terms = extract_product_terms(user_message)
    if not search_terms:
        return None, "I couldn't find an order number in your message. " \
                   "Could you please provide the order number or be more specific about the product?"
    
    # Search for orders with matching product names
    result = find_orders_by_product_name(user_id, search_terms, status='shipped')
    
    if not result['success'] or not result.get('matches'):
        return None, "I couldn't find any matching orders. Could you please provide the order number?"
    
    matches = result['matches']
    
    # If exactly one match found, confirm it
    if len(matches) == 1:
        order = matches[0]
        return order['order_id'], f"I found an order for {order['product_name']}. " \
                                f"Is this the order you're referring to?"
    
    # If multiple matches found, list them for the user to choose
    response = ["I found multiple orders that might match:"]
    for i, order in enumerate(matches[:5], 1):  # Limit to top 5 matches
        response.append(f"{i}. {format_order_suggestion(order)}")
    
    response.append("\nPlease specify which order you're referring to by number or provide more details.")
    return None, "\n".join(response)

def extract_product_terms(message: str) -> List[str]:
    """Extract potential product names/terms from a message."""
    # Common words to ignore
    stop_words = {
        'my', 'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his',
        'she', 'her', 'hers', 'it', 'its', 'we', 'us', 'our', 'ours', 'they',
        'them', 'their', 'theirs', 'this', 'that', 'these', 'those', 'there',
        'here', 'where', 'when', 'how', 'what', 'which', 'who', 'whom',
        'whose', 'why', 'can', 'could', 'would', 'should', 'may', 'might',
        'must', 'shall', 'will', 'have', 'has', 'had', 'having', 'be', 'been',
        'being', 'do', 'does', 'did', 'doing', 'to', 'for', 'with', 'about',
        'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'from', 'down', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
        'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
        'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't",
        'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
        "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
        "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
        "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
        'wouldn', "wouldn't"
    }
    
    # Extract words that might be part of product names
    words = re.findall(r'\b[\w\-]+\b', message.lower())
    
    # Filter out stop words and short words
    product_terms = [
        word for word in words 
        if word not in stop_words and len(word) > 2
    ]
    
    return product_terms

def confirm_order_selection(user_input: str, matches: List[Dict]) -> Tuple[Optional[int], str]:
    """
    Parse user's selection from multiple order matches.
    
    Args:
        user_input: User's response to the order selection prompt
        matches: List of order matches from find_orders_by_product_name
        
    Returns:
        Tuple of (order_id, response_message)
    """
    # Check if user selected a number
    try:
        selection = int(user_input.strip())
        if 1 <= selection <= len(matches):
            return matches[selection-1]['order_id'], ""
    except (ValueError, IndexError):
        pass
    
    # Check if user said 'yes' to a single suggestion
    if len(matches) == 1 and user_input.lower().strip() in ('y', 'yes', 'yeah', 'yep'):
        return matches[0]['order_id'], ""
    
    # If we get here, the selection wasn't valid
    return None, "I'm sorry, I didn't understand your selection. Please try again."
