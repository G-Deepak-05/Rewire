"""
AI Coach schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None  # None = new conversation


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    conversation_title: str


class ConversationListItem(BaseModel):
    id: UUID
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    conversations: list[ConversationListItem]
    total: int


class ConversationDetailResponse(BaseModel):
    id: UUID
    title: str
    messages: list[dict]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
