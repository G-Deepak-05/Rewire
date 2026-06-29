"""Conversation repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.conversation import Conversation
from app.repositories.base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    async def get_by_user(self, user_id: UUID, limit: int = 20) -> list[Conversation]:
        """Get recent conversations for a user."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
