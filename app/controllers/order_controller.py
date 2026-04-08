from fastapi import Depends, HTTPException

from app.controllers.abstract_controller import AbstractController
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.services.order_service import OrderService
from app.schemas import OrderResponse


def get_order_repository() -> OrderRepository:
    return OrderRepository()


def get_product_repository() -> ProductRepository:
    return ProductRepository()


def get_cart_repository() -> CartRepository:
    return CartRepository()


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    cart_repo: CartRepository = Depends(get_cart_repository),
) -> OrderService:
    return OrderService(order_repo, product_repo, cart_repo)


class OrderController(AbstractController[OrderResponse]):
    def __init__(self, service: OrderService = Depends(get_order_service)):
        super().__init__(service)
        self.service = service

    async def create(self, user_id: str) -> OrderResponse:
        try:
            return await self.service.create_order(user_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_by_id(self, id: str) -> OrderResponse:
        order = await self.service.get_order_by_id(id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def get_all(self, page: int = 1, limit: int = 10) -> list:
        return await self.service.get_all_orders(page, limit)

    async def get_user_orders(self, user_id: str, page: int = 1, limit: int = 10) -> list:
        return await self.service.get_user_orders(user_id, page, limit)

    async def update(self, id: str, data: dict) -> bool:
        return await self.service.update_order_status(id, data.get("status"))

    async def delete(self, id: str) -> bool:
        # Orders typically shouldn't be deleted
        raise HTTPException(status_code=403, detail="Cannot delete orders")
