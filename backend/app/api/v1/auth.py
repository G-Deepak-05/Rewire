"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    svc = AuthService(db)
    return await svc.register(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT tokens."""
    svc = AuthService(db)
    return await svc.login(email=request.email, password=request.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Rotate refresh token and get new access token."""
    svc = AuthService(db)
    return await svc.refresh(request.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke refresh token."""
    svc = AuthService(db)
    await svc.logout(request.refresh_token)
    return {"message": "Logged out successfully"}
