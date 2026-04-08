from typing import Any, Generic, List, Optional, TypeVar

from app.controllers.base_controller import BaseControllerInterface

T = TypeVar("T")


class AbstractController(BaseControllerInterface[T], Generic[T]):
    """Abstract base controller with common logic"""

    def __init__(self, service):
        self.service = service

    async def create(self, data: Any) -> T:
        return await self.service.create(data)

    async def get_by_id(self, id: str) -> Optional[T]:
        return await self.service.get_by_id(id)

    async def get_all(self, **kwargs) -> List[T]:
        return await self.service.get_all(**kwargs)

    async def update(self, id: str, data: Any) -> bool:
        return await self.service.update(id, data)

    async def delete(self, id: str) -> bool:
        return await self.service.delete(id)
