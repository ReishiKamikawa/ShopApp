from typing import List, Optional

from bson import ObjectId

from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__("products")

    async def create(self, data: dict) -> dict:
        result = await self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    async def get_by_id(self, id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def get_all(self, skip: int = 0, limit: int = 10, sort: str = "created_at") -> List[dict]:
        cursor = self.collection.find().sort(sort, -1).skip(skip).limit(limit)
        return await cursor.to_list(length=None)

    async def search(self, query: str, skip: int = 0, limit: int = 10) -> List[dict]:
        cursor = self.collection.find({"$text": {"$search": query}}).skip(skip).limit(limit)
        return await cursor.to_list(length=None)

    async def update(self, id: str, data: dict) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def decrease_stock(self, id: str, quantity: int) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(id), "stock": {"$gte": quantity}},
            {"$inc": {"stock": -quantity}}
        )
        return result.modified_count > 0
