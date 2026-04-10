from fastapi import APIRouter, Depends, Header, HTTPException

from app.controllers.order_controller import OrderController, get_order_service
from app.schemas import OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_user_id_from_header(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Missing authorization header")
    from app.core.security import decode_access_token
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid token")


@router.post("", response_model=OrderResponse, status_code=201, summary="Create order from cart")
async def create_order(
    user_id: str = Depends(get_user_id_from_header),
    service: OrderService = Depends(get_order_service)
):
    """
    Create an order from the user's cart items.

    **Required:** Authorization header with Bearer token

    **Successful example:**
    - User must have items in cart
    - Authorization: Bearer <valid_token>

    **Failure cases:**
    - Missing Authorization header: Returns 401
    - Invalid token: Returns 401
    - Cart is empty: Returns 400
    - Insufficient stock: Returns 400
    """
    try:
        return await service.create_order(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order by ID")
async def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """
    Get order details by order ID.

    **Path parameters:**
    - order_id: Order ID (from create order response)

    **Successful example:**
    - order_id: "507f1f77bcf86cd799439013"

    **Failure cases:**
    - Non-existent order: Returns 404
    - Invalid order ID format: Returns 400
    """
    try:
        order = await service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        # Re-raise FastApi's HTTPException so it's not caught by the broad Exception block
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid order ID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid order ID format")


@router.get("", response_model=list, summary="List user orders")
async def list_orders(
    page: int = 1,
    limit: int = 10,
    user_id: str = Depends(get_user_id_from_header),
    service: OrderService = Depends(get_order_service)
):
    """
    Get user's orders with pagination.

    **Required:** Authorization header with Bearer token

    **Query parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)

    **Successful example:**
    - page=1, limit=10
    - Authorization: Bearer <valid_token>

     **Failure cases:**
    - Missing Authorization header: Returns 401
    - Invalid page/limit values: Returns validation error
    """
    try:
        return await service.get_user_orders(user_id, page, limit)
    except Exception as e:
        # Log error and return empty list for now
        print(f"Error in list_orders: {e}")
        return []
