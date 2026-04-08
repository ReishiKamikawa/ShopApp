from fastapi import Depends, HTTPException

from app.controllers.abstract_controller import AbstractController
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.schemas import ProductCreate, ProductResponse, ProductUpdate


def get_product_repository() -> ProductRepository:
    return ProductRepository()


def get_product_service(repo: ProductRepository = Depends(get_product_repository)) -> ProductService:
    return ProductService(repo)


class ProductController(AbstractController[ProductResponse]):
    def __init__(self, service: ProductService = Depends(get_product_service)):
        super().__init__(service)
        self.service = service

    async def create(self, data: ProductCreate) -> ProductResponse:
        return await self.service.create_product(data)

    async def get_by_id(self, id: str) -> ProductResponse:
        product = await self.service.get_product_by_id(id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def get_all(self, page: int = 1, limit: int = 10, sort: str = "created_at") -> list:
        return await self.service.get_all_products(page, limit, sort)

    async def search(self, query: str, skip: int = 0, limit: int = 10) -> list:
        return await self.service.search_products(query, skip, limit)

    async def update(self, id: str, data: ProductUpdate) -> bool:
        success = await self.service.update_product(id, data)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return success

    async def delete(self, id: str) -> bool:
        success = await self.service.delete_product(id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return success
