"""
Journal endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.schemas.journal import (
    JournalCreateRequest,
    JournalEntryResponse,
    JournalListResponse,
    JournalStatsResponse,
)
from app.services.journal_service import JournalService

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    data: JournalCreateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a context-rich journal entry. AI responds contextually."""
    svc = JournalService(db)
    return await svc.create_entry(current_user.id, data)


@router.get("", response_model=JournalListResponse)
async def list_journal_entries(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated journal entries."""
    svc = JournalService(db)
    return await svc.get_entries(current_user.id, offset, limit)


@router.get("/stats", response_model=JournalStatsResponse)
async def get_journal_stats(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated journal statistics."""
    svc = JournalService(db)
    return await svc.get_stats(current_user.id)


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single journal entry."""
    svc = JournalService(db)
    return await svc.get_entry(current_user.id, entry_id)
