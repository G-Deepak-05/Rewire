"""
Auth service — registration, login, token management.
"""

from datetime import UTC, datetime, timedelta
import hashlib

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, InvalidTokenError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, email: str, password: str, display_name: str | None = None) -> dict:
        """Register a new user."""
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("Email already registered")

        user = await self.user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            display_name=display_name or email.split("@")[0],
        )

        tokens = await self._create_tokens(user.id)
        logger.info("User registered", user_id=str(user.id), email=email)
        return tokens

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        tokens = await self._create_tokens(user.id)
        logger.info("User logged in", user_id=str(user.id))
        return tokens

    async def refresh(self, refresh_token: str) -> dict:
        """Rotate refresh token and issue new access token."""
        try:
            payload = decode_refresh_token(refresh_token)
        except JWTError:
            raise InvalidTokenError("Invalid refresh token") from None

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored_token = await self.token_repo.get_by_token_hash(token_hash)
        if not stored_token:
            raise InvalidTokenError("Refresh token not found or revoked")

        # Revoke old token
        await self.token_repo.update(stored_token, is_revoked=True)

        # Issue new pair
        from uuid import UUID
        user_id = UUID(payload["sub"])
        return await self._create_tokens(user_id)

    async def logout(self, refresh_token: str) -> None:
        """Revoke the refresh token."""
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored_token = await self.token_repo.get_by_token_hash(token_hash)
        if stored_token:
            await self.token_repo.update(stored_token, is_revoked=True)

    async def _create_tokens(self, user_id) -> dict:
        """Create access + refresh token pair and store refresh token hash."""
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # Store refresh token hash
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        await self.token_repo.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
