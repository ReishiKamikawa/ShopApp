from fastapi import Depends, HTTPException, status
from datetime import timedelta

from app.core.security import create_access_token, decode_access_token
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


class AuthController:
    def __init__(self, user_service: UserService = Depends(get_user_service)):
        self.user_service = user_service

    async def register(self, user_data: UserCreate) -> UserResponse:
        try:
            user = await self.user_service.create_user(user_data)
            return user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def login(self, user_data: UserLogin) -> Token:
        user = await self.user_service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: str) -> dict:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": user_id, "role": role}
