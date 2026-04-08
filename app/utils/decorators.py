from datetime import datetime
from typing import Optional


class AuditLog:
    @staticmethod
    async def log_action(
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Optional[dict] = None
    ):
        """Log user actions for audit trail"""
        db = None  # Would be injected in production

        log_entry = {
            "user_id": user_id,
            "action": action,  # create, read, update, delete
            "entity_type": entity_type,  # user, product, order, etc
            "entity_id": entity_id,
            "changes": changes,
            "timestamp": datetime.utcnow()
        }

        # Save to MongoDB audit_logs collection
        # await db["audit_logs"].insert_one(log_entry)
        print(f"📋 Audit: {log_entry}")


class RateLimiter:
    @staticmethod
    async def check_rate_limit(redis, user_id: str, limit: int = 100, window: int = 60):
        """Check if user exceeded rate limit"""
        key = f"rate_limit:{user_id}"
        count = await redis.incr(key)

        if count == 1:
            await redis.expire(key, window)

        return count <= limit
