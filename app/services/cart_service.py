from typing import Optional

from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas import CartResponse, CartItemCreate


class CartService:
    def __init__(self, cart_repository: CartRepository, product_repository: ProductRepository):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    async def get_cart(self, user_id: str) -> Optional[CartResponse]:
        cart = await self.cart_repository.get_by_user_id(user_id)
        if cart:
            return CartResponse(**cart)
        return None

    async def add_to_cart(self, user_id: str, item_data: CartItemCreate) -> CartResponse:
        # Validate product exists
        product = await self.product_repository.get_by_id(item_data.product_id)
        if not product:
            raise ValueError("Product not found")
        
        cart = await self.cart_repository.add_item(user_id, item_data.product_id, item_data.quantity)
        return CartResponse(**cart)

    async def remove_from_cart(self, user_id: str, product_id: str) -> CartResponse:
        cart = await self.cart_repository.remove_item(user_id, product_id)
        if cart:
            return CartResponse(**cart)
        # Return empty cart
        return CartResponse(id=None, user_id=user_id, items=[], updated_at=None)
