from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseControllerInterface(ABC, Generic[T]):
    """Base interface for all controllers"""

    @abstractmethod
    async def create(self, data: Any) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, **kwargs) -> List[T]:
        pass

    @abstractmethod
    async def update(self, id: str, data: Any) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
