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


from fastapi import APIRouter, Depends, BackgroundTasks

async def generate_plan_background(user_id):
    from app.db.session import AsyncSessionLocal
    from app.services.plan_service import PlanService
    
    async with AsyncSessionLocal() as db:
        plan_svc = PlanService(db)
        await plan_svc.generate_plan(user_id)

@router.post("/profile", response_model=OnboardingResponse, status_code=201)
async def submit_onboarding(
    data: OnboardingRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding profile data."""
    svc = UserService(db)
    profile = await svc.submit_onboarding(current_user.id, data)
    
    # Explicitly commit the transaction so the background task can read the profile
    # before the background task runs (BackgroundTasks run before dependency teardown)
    await db.commit()
    
    background_tasks.add_task(generate_plan_background, current_user.id)
    return profile


@router.patch("/profile", response_model=OnboardingResponse)
async def update_onboarding(
    data: OnboardingRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update onboarding profile."""
    svc = UserService(db)
    return await svc.update_onboarding(current_user.id, data)


@router.get("/profile", response_model=OnboardingResponse)
async def get_profile(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's onboarding profile."""
    svc = UserService(db)
    return await svc.get_profile(current_user.id)
