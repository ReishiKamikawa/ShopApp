from typing import List, Optional
from datetime import datetime

from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserResponse


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Check if email exists
        existing = await self.user_repository.get_by_email(user_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict["password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user = await self.user_repository.create(user_dict)
        return UserResponse(**user)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user["password"]):
            return None
        return UserResponse(**user)

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_id(user_id)
        if user:
            return UserResponse(**user)
        return None

    async def get_all_users(self, skip: int = 0, limit: int = 10) -> List[UserResponse]:
        users = await self.user_repository.get_all(skip, limit)
        return [UserResponse(**user) for user in users]

    async def update_user(self, user_id: str, update_data: dict) -> bool:
        return await self.user_repository.update(user_id, update_data)

    async def delete_user(self, user_id: str) -> bool:
        return await self.user_repository.delete(user_id)
