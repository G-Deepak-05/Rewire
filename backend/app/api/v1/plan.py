from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plan", tags=["Recovery Plan"])


@router.get("")
async def get_plan(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's recovery plan."""
    svc = PlanService(db)
    return await svc.get_plan(current_user.id)


@router.post("/task")
async def toggle_task(
    day: int,
    task: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a task for a specific day."""
    svc = PlanService(db)
    return await svc.toggle_task(current_user.id, day, task)
