from typing import List, Optional

from app.db.redis import get_redis
from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate, ProductResponse, ProductUpdate


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.redis = get_redis()

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        product = await self.product_repository.create(product_data.dict())
        # Invalidate cache
        await self._invalidate_product_cache()
        # Publish event
        await self.redis.publish("product.created", f"{product['_id']}")
        return ProductResponse(**product)

    async def get_product_by_id(self, product_id: str) -> Optional[ProductResponse]:
        # Try cache first
        cache_key = f"product:{product_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            import json
            return ProductResponse(**json.loads(cached))
        
        product = await self.product_repository.get_by_id(product_id)
        if product:
            # Cache it - product is already a dict
            import json
            try:
                await self.redis.setex(cache_key, 60, json.dumps(product))
            except Exception:
                pass  # Cache failure is not critical
            return ProductResponse(**product)
        return None

    async def get_all_products(self, page: int = 1, limit: int = 10, sort: str = "created_at") -> List[ProductResponse]:
        skip = (page - 1) * limit
        cache_key = f"products:page:{page}:limit:{limit}:sort:{sort}"
        cached = await self.redis.get(cache_key)
        if cached:
            import json
            products = json.loads(cached)
            return [ProductResponse(**p) for p in products]
        
        products = await self.product_repository.get_all(skip, limit, sort)
        # Cache - products are already dicts from repository
        import json
        try:
            await self.redis.setex(cache_key, 60, json.dumps(products))
        except Exception:
            pass  # Cache failure is not critical
        return [ProductResponse(**p) for p in products]

    async def search_products(self, query: str, skip: int = 0, limit: int = 10) -> List[ProductResponse]:
        products = await self.product_repository.search(query, skip, limit)
        return [ProductResponse(**p) for p in products]

    async def update_product(self, product_id: str, update_data: ProductUpdate) -> bool:
        success = await self.product_repository.update(product_id, update_data.dict(exclude_unset=True))
        if success:
            # Invalidate cache
            await self._invalidate_product_cache(product_id)
            # Publish event
            await self.redis.publish("product.updated", product_id)
        return success

    async def delete_product(self, product_id: str) -> bool:
        success = await self.product_repository.delete(product_id)
        if success:
            await self._invalidate_product_cache(product_id)
            # Publish event
            await self.redis.publish("product.deleted", product_id)
        return success

    async def _invalidate_product_cache(self, product_id: str = None):
        if product_id:
            await self.redis.delete(f"product:{product_id}")
        # Invalidate list caches (simplified)
        keys = await self.redis.keys("products:*")
        if keys:
            await self.redis.delete(*keys)
