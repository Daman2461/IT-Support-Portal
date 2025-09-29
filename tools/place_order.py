from datetime import datetime
from db.schema import SessionLocal, Order, OrderStatus, db
from audit.logger import log_action

def place_order(product_name: str, product_id: str, amount: float, 
               shipping_address: str, user_id: int, status: str = OrderStatus.PENDING.value):
    """
    Create a new order in the system.
    
    Args:
        product_name: Name of the product (required)
        product_id: Unique identifier for the product (required)
        amount: Total amount in USD (must be greater than 0)
        shipping_address: Complete delivery address (required)
        user_id: ID of the user placing the order (required)
        status: Order status (default: Pending)
        
    Returns:
        dict: Result of the order creation with order details or error message
        {
            "success": bool,
            "order_id": int (if successful),
            "message": str,
            "error": str (if failed)
        }
    """
    # Input validation
    if not product_name or not isinstance(product_name, str):
        return {"success": False, "error": "Product name is required and must be a string"}
    if not product_id or not isinstance(product_id, str):
        return {"success": False, "error": "Product ID is required and must be a string"}
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {"success": False, "error": "Amount must be a number greater than zero"}
    if not shipping_address or not isinstance(shipping_address, str) or len(shipping_address.strip()) < 10:
        return {"success": False, "error": "A complete shipping address is required"}
    if not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "error": "A valid user ID is required"}

    session = SessionLocal()
    try:
        # Additional validation
        if not product_name.strip():
            raise ValueError("Product name cannot be empty")
            
        # Create a new order
        new_order = Order(
            product_name=product_name,
            product_id=product_id,
            amount=amount,
            shipping_address=shipping_address,
            user_id=user_id,  # Set the user_id from the session
            status=status,
            order_date=datetime.utcnow()
        )
        
        # Add to database
        session.add(new_order)
        session.commit()
        
        # Prepare response
        response = {
            "success": True,
            "order_id": new_order.id,
            "status": new_order.status,
            "order_date": new_order.order_date.isoformat(),
            "message": f"Order #{new_order.id} for {product_name} has been created successfully."
        }
        
        # Log the action
        log_action("order_created", 
                 {"order_id": new_order.id, "product_name": product_name, "amount": amount},
                 response)
        
        return response
        
    except Exception as e:
        session.rollback()
        error_msg = f"Error creating order: {str(e)}"
        result = {"success": False, "error": error_msg}
        log_action("order_creation_failed", 
                 {"product_name": product_name, "error": str(e)}, 
                 result)
        return result
        
    finally:
        session.close()
