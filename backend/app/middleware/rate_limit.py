"""
Rate limiting middleware using Redis sliding window.
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple Redis-based rate limiter (sliding window)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and docs
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/metrics", "/api/v1/health"):
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        try:
            from app.core.dependencies import get_redis

            redis = await get_redis()
            key = f"ratelimit:{client_ip}"
            current = await redis.get(key)

            if current and int(current) >= settings.rate_limit_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "status_code": 429,
                    },
                )

            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            await pipe.execute()

        except Exception:
            # If Redis is down, don't block requests
            pass

        return await call_next(request)
