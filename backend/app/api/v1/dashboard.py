"""
Dashboard endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.schemas.dashboard import (
    DashboardResponse,
    InsightsResponse,
    RecoveryScoreHistoryResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full recovery dashboard data."""
    svc = DashboardService(db)
    return await svc.get_dashboard(current_user.id)


@router.get("/score/history", response_model=RecoveryScoreHistoryResponse)
async def get_score_history(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recovery score history over time."""
    svc = DashboardService(db)
    return await svc.get_score_history(current_user.id)


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated behavioral insights."""
    svc = DashboardService(db)
    return await svc.get_insights(current_user.id)
