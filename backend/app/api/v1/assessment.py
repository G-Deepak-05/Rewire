"""
Assessment endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.schemas.assessment import (
    AssessmentHistoryResponse,
    AssessmentResultResponse,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmitRequest,
)
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessment", tags=["Assessment"])


@router.post("/start", response_model=AssessmentStartResponse)
async def start_assessment(
    data: AssessmentStartRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Begin an addiction assessment — returns tailored questions."""
    svc = AssessmentService(db)
    return await svc.start_assessment(current_user.id, data.addiction_type)


@router.post("/submit", response_model=AssessmentResultResponse)
async def submit_assessment(
    data: AssessmentSubmitRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit assessment answers — computes scores and AI analysis."""
    svc = AssessmentService(db)
    return await svc.submit_assessment(current_user.id, data.assessment_id, data.responses)


@router.get("/history", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get past assessments with trend data."""
    svc = AssessmentService(db)
    return await svc.get_history(current_user.id)
