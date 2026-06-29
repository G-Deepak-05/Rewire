"""
API v1 aggregate router.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.assessment import router as assessment_router
from app.api.v1.coach import router as coach_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.health import router as health_router
from app.api.v1.journal import router as journal_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.users import router as users_router

router = APIRouter()

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(onboarding_router)
router.include_router(assessment_router)
router.include_router(journal_router)
router.include_router(coach_router)
router.include_router(dashboard_router)
router.include_router(emergency_router)
