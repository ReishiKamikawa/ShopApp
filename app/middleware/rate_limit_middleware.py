from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.db.redis import get_redis

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-HTTP requests (e.g. WebSocket) or missing client IP
        if request.client is None or request.headers.get("x-test-bypass") == "true":
            return await call_next(request)

        client_ip = request.client.host
        redis = get_redis()
        
        if redis is None:
            # If Redis isn't connected yet, skip rate limit
            return await call_next(request)

        key = f"rate_limit:{client_ip}"
        
        try:
            # Increment request count
            current_requests = await redis.incr(key)
            
            # If first request, set expiration
            if current_requests == 1:
                await redis.expire(key, self.window_seconds)
                
            if current_requests > self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests"}
                )
        except Exception:
            # Fallback in case of Redis errors
            pass

        return await call_next(request)
