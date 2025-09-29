from db.schema import SessionLocal, Order, OrderStatus
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import or_

def find_orders_by_user(user_id: int, product_name: str = None, include_address: bool = True) -> Dict[str, Any]:
    """
    Get a list of orders for a specific user with optional filtering.
    
    Args:
        user_id: The ID of the user whose orders to find (required)
        product_name: Optional product name to filter by (case-insensitive)
        include_address: Whether to include shipping address in the results
        
    Returns:
        Dictionary containing:
        - success: bool indicating if the operation was successful
        - orders: List of orders (empty if none found)
        - latest_shipping_address: The most recent shipping address used (if any)
        - error: Error message if success is False
    """
    if not user_id:
        return {
            'success': False,
            'error': 'User ID is required',
            'orders': [],
            'latest_shipping_address': None
        }
        
    session = SessionLocal()
    try:
        # Build the base query
        query = session.query(Order).filter(Order.user_id == user_id)
        
        # Apply product name filter if provided
        if product_name and product_name.strip():
            query = query.filter(Order.product_name.ilike(f'%{product_name}%'))
        
        # Get orders sorted by most recent first
        orders = query.order_by(Order.order_date.desc()).all()
        
        # Format the orders
        formatted_orders = []
        latest_address = None
        
        for order in orders:
            order_data = {
                'id': order.id,
                'product': order.product_name or 'Unknown',
                'amount': float(order.amount) if order.amount else 0.0,
                'status': (order.status or 'unknown').replace('_', ' ').title(),
                'date': order.order_date.strftime('%Y-%m-%d') if order.order_date else 'N/A'
            }
            
            # Include address if requested and available
            if include_address and order.shipping_address:
                order_data['shipping_address'] = order.shipping_address
                # Set the latest address from the most recent order
                if not latest_address and order.shipping_address:
                    latest_address = order.shipping_address
            
            formatted_orders.append(order_data)
        
        return {
            'success': True,
            'orders': formatted_orders,
            'latest_shipping_address': latest_address,
            'total_orders': len(formatted_orders)
        }
        
    except Exception as e:
        return [{
            'error': f"Error finding orders: {str(e)}",
            'success': False
        }]
    finally:
        session.close()
