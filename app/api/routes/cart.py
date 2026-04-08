from fastapi import APIRouter, Depends, Header, HTTPException

from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.services.cart_service import CartService
from app.schemas import CartResponse, CartItemCreate

router = APIRouter(prefix="/cart", tags=["cart"])


def get_cart_repository() -> CartRepository:
    return CartRepository()


def get_product_repository() -> ProductRepository:
    return ProductRepository()


def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> CartService:
    return CartService(cart_repo, product_repo)


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


@router.get("", response_model=CartResponse, summary="Get user cart")
async def get_cart(
    user_id: str = Depends(get_user_id_from_header),
    service: CartService = Depends(get_cart_service)
):
    """
    Get current user's shopping cart.

    **Required:** Authorization header with Bearer token (get from /auth/login)

    **Successful example:**
    - Authorization: Bearer <valid_token>

    **Failure cases:**
    - Missing Authorization header: Returns 401
    - Invalid token: Returns 401
    - Cart not found: Returns 404
    """
    cart = await service.get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.post("/add", response_model=CartResponse, summary="Add item to cart")
async def add_to_cart(
    item: CartItemCreate,
    user_id: str = Depends(get_user_id_from_header),
    service: CartService = Depends(get_cart_service)
):
    """
    Add a product to user's cart.

    **Required:** Authorization header with Bearer token

    **Successful example:**
    - product_id: "507f1f77bcf86cd799439011" (valid product ID)
    - quantity: 2

    **Failure cases:**
    - Missing Authorization header: Returns 401
    - Invalid product ID: Returns 400
    - Product doesn't exist: Returns 400
    - Quantity <= 0: Returns validation error
    - Stock not available: Returns 400
    """
    try:
        return await service.add_to_cart(user_id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/remove", response_model=CartResponse, summary="Remove item from cart")
async def remove_from_cart(
    product_id: str,
    user_id: str = Depends(get_user_id_from_header),
    service: CartService = Depends(get_cart_service)
):
    """
    Remove a product from user's cart.

    **Required:** Authorization header with Bearer token

    **Query parameters:**
    - product_id: Product ID to remove

    **Successful example:**
    - product_id: "507f1f77bcf86cd799439011"

    **Failure cases:**
    - Missing Authorization header: Returns 401
    - Product not in cart: May return error or empty response
    """
    return await service.remove_from_cart(user_id, product_id)
