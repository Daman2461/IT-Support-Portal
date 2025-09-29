from typing import List, Dict, Optional
from db.schema import SessionLocal, Order, OrderStatus
from datetime import datetime, timedelta

def find_orders_by_product_name(user_id: int, search_terms: Optional[List[str]] = None, status: Optional[str] = None) -> Dict:
    """
    Search for orders by product name and optional status.
    
    Args:
        user_id: ID of the user whose orders to search
        search_terms: List of search terms to look for in product names (default: [])
        status: Optional order status to filter by (e.g., 'shipped')
    
    Returns:
        Dictionary with search results and potential matches
    """
    # Handle case when search_terms is None
    if search_terms is None:
        search_terms = []
        
    session = SessionLocal()
    try:
        # Build the base query
        query = session.query(Order).filter(
            Order.user_id == user_id,
            Order.product_name.isnot(None)
        )
        
        # Add status filter if provided
        if status:
            query = query.filter(Order.status == status.upper())
        
        # Get all potential matching orders
        all_orders = query.order_by(Order.order_date.desc()).all()
        
        # Find orders that match any of the search terms
        matches = []
        for order in all_orders:
            if not order.product_name:
                continue
                
            # If no search terms, include all orders
            if not search_terms:
                matches.append({
                    'order_id': order.id,
                    'product_name': order.product_name,
                    'status': order.status,
                    'order_date': order.order_date.strftime('%Y-%m-%d'),
                    'amount': order.amount
                })
                continue
                
            # Check if any search term is in the product name (case insensitive)
            product_lower = order.product_name.lower()
            for term in search_terms:
                if term and term.lower() in product_lower:
                    matches.append({
                        'order_id': order.id,
                        'product_name': order.product_name,
                        'status': order.status,
                        'order_date': order.order_date.strftime('%Y-%m-%d'),
                        'amount': order.amount
                    })
                    break  # No need to check other terms for this order
        
        # Return a properly formatted response
        if not matches:
            return {
                'success': False,
                'error': 'No matching orders found',
                'suggestions': []
            }
            
        return {
            'success': True,
            'matches': matches,
            'message': f"Found {len(matches)} matching order(s)"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error searching orders: {str(e)}",
            'suggestions': []
        }
    finally:
        session.close()

def format_order_suggestion(order: Dict) -> str:
    """Format an order for display to the user."""
    return (
        f"Order #{order['order_id']}: {order['product_name']} | "
        f"Status: {order['status'].title()} | "
        f"Date: {order['order_date']} | "
        f"Amount: ${order['amount']:.2f}"
    )
