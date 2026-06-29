"""
Onboarding endpoints — multi-step profile setup.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.schemas.user import OnboardingRequest, OnboardingResponse, OnboardingStatusResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if onboarding is completed."""
    svc = UserService(db)
    return await svc.get_onboarding_status(current_user.id)


@router.post("/profile", response_model=OnboardingResponse, status_code=201)
async def submit_onboarding(
    data: OnboardingRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding profile data."""
    svc = UserService(db)
    return await svc.submit_onboarding(current_user.id, data)


@router.patch("/profile", response_model=OnboardingResponse)
async def update_onboarding(
    data: OnboardingRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update onboarding profile."""
    svc = UserService(db)
    return await svc.update_onboarding(current_user.id, data)
