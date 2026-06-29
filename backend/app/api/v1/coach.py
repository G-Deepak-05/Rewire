"""
AI Coach chat endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.schemas.coach import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationListResponse,
)
from app.schemas.auth import MessageResponse
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["AI Coach"])


from fastapi.responses import StreamingResponse

@router.post("/chat", response_model=ChatResponse)
async def chat_with_coach(
    data: ChatRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI recovery coach."""
    svc = CoachService(db)
    return await svc.chat(current_user.id, data.message, data.conversation_id)


@router.post("/stream")
async def stream_coach_response(
    data: ChatRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream a message to the AI recovery coach."""
    svc = CoachService(db)
    return StreamingResponse(
        svc.stream_chat(current_user.id, data.message, data.conversation_id),
        media_type="text/event-stream"
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all AI coach conversations."""
    svc = CoachService(db)
    return await svc.get_conversations(current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full conversation history."""
    svc = CoachService(db)
    return await svc.get_conversation(current_user.id, conversation_id)


@router.delete("/conversations/{conversation_id}", response_model=MessageResponse)
async def delete_conversation(
    conversation_id: UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation."""
    svc = CoachService(db)
    await svc.delete_conversation(current_user.id, conversation_id)
    return {"message": "Conversation deleted"}
