"""
FastAPI dependency injection factories.
Provides reusable dependencies for DB sessions, Redis, authentication.
"""

from typing import Annotated
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, InvalidTokenError
from app.core.logging import get_logger
from app.core.security import decode_access_token
from app.db.session import get_db

logger = get_logger(__name__)

# ─── HTTP Bearer scheme ───────────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)

# ─── Redis ────────────────────────────────────────────────────────────────────
_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return a shared async Redis client."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _redis_pool


# ─── Current User ─────────────────────────────────────────────────────────────
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Extract and validate JWT Bearer token, return current user."""
    from app.repositories.user_repository import UserRepository

    if not credentials:
        raise AuthenticationError("Authorization header missing")

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise InvalidTokenError() from None

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Token missing subject claim")

    repo = UserRepository(db)
    user = await repo.get(UUID(user_id))
    if not user:
        raise AuthenticationError("User not found")

    return user


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    """Ensure the current user account is active."""
    if not current_user.is_active:
        raise AuthenticationError("Account is deactivated")
    return current_user


# ─── Type aliases ─────────────────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[aioredis.Redis, Depends(get_redis)]
CurrentUser = Annotated[object, Depends(get_current_active_user)]
