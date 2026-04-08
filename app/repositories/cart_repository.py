from typing import List, Optional

from bson import ObjectId

from app.repositories.base_repository import BaseRepository


class CartRepository(BaseRepository):
    def __init__(self):
        super().__init__("carts")

    async def create(self, data: dict) -> dict:
        result = await self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    async def get_by_id(self, id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def get_by_user_id(self, user_id: str) -> Optional[dict]:
        return await self.collection.find_one({"user_id": ObjectId(user_id)})

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=None)

    async def update(self, id: str, data: dict) -> bool:
        result = await self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def add_item(self, user_id: str, product_id: str, quantity: int) -> dict:
        from datetime import datetime
        from bson import ObjectId as BsonObjectId

        cart = await self.get_by_user_id(user_id)
        if not cart:
            cart = await self.create({
                "user_id": BsonObjectId(user_id),
                "items": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

        # Check if item exists
        item_exists = False
        for item in cart["items"]:
            if str(item["product_id"]) == product_id:
                item["quantity"] += quantity
                item_exists = True
                break
        if not item_exists:
            cart["items"].append({"product_id": BsonObjectId(product_id), "quantity": quantity})

        cart["updated_at"] = datetime.utcnow()
        await self.update(str(cart["_id"]), cart)
        return cart

    async def remove_item(self, user_id: str, product_id: str) -> dict:
        from datetime import datetime

        cart = await self.get_by_user_id(user_id)
        if cart:
            cart["items"] = [item for item in cart["items"] if str(item["product_id"]) != product_id]
            cart["updated_at"] = datetime.utcnow()
            await self.update(str(cart["_id"]), cart)
        return cart

    async def clear_cart(self, user_id: str) -> bool:
        cart = await self.get_by_user_id(user_id)
        if cart:
            return await self.delete(str(cart["_id"]))
        return True
