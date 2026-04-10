from typing import List, Optional
from datetime import datetime

from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserResponse
from app.db.redis import get_redis


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.redis = get_redis()

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Check if email exists
        existing = await self.user_repository.get_by_email(user_data.email)
        if existing:
            raise ValueError("Email already registered")
        
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        import random
        import json
        
        user_dict["password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["is_verified"] = False
        user = await self.user_repository.create(user_dict)
        
        # Generate random 6-digit OTP
        otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store OTP in Redis with 5 minutes expiration
        await self.redis.setex(f"otp:{user_data.email}", 300, otp_code)
        
        # Publish OTP Requested Event (simulate sending email)
        event_payload = json.dumps({"email": user_data.email, "otp": otp_code})
        await self.redis.publish("user.otp_requested", event_payload)
        
        # Publish regular audit event
        await self.redis.publish("user.created", f"{user['_id']}")
        return UserResponse(**user)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user["password"]):
            return None
            
        if not user.get("is_verified", False):
            raise ValueError("Account not verified. Please verify your OTP.")
            
        return UserResponse(**user)

    async def verify_otp(self, email: str, otp_code: str) -> bool:
        # Check Redis for the OTP
        stored_otp = await self.redis.get(f"otp:{email}")
        if not stored_otp or stored_otp.decode() != otp_code:
            return False
            
        # Get user to update
        user = await self.user_repository.get_by_email(email)
        if not user:
            return False
            
        # Update is_verified to True
        success = await self.user_repository.update(str(user["_id"]), {"is_verified": True})
        if success:
            # Clear the OTP from Redis
            await self.redis.delete(f"otp:{email}")
            await self.redis.publish("user.verified", str(user["_id"]))
            return True
        return False

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_id(user_id)
        if user:
            return UserResponse(**user)
        return None

    async def get_all_users(self, skip: int = 0, limit: int = 10) -> List[UserResponse]:
        users = await self.user_repository.get_all(skip, limit)
        return [UserResponse(**user) for user in users]

    async def update_user(self, user_id: str, update_data: dict) -> bool:
        success = await self.user_repository.update(user_id, update_data)
        if success:
            await self.redis.publish("user.updated", user_id)
        return success

    async def delete_user(self, user_id: str) -> bool:
        success = await self.user_repository.delete(user_id)
        if success:
            await self.redis.publish("user.deleted", user_id)
        return success
