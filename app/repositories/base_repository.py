from abc import ABC, abstractmethod
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongodb import get_database


class BaseRepository(ABC):
    def __init__(self, collection_name: str):
        self.collection: AsyncIOMotorCollection = get_database()[collection_name]

    @abstractmethod
    async def create(self, data: dict) -> dict:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[dict]:
        pass

    @abstractmethod
    async def update(self, id: str, data: dict) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
