"""Trigger repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.trigger import Trigger
from app.repositories.base_repository import BaseRepository


class TriggerRepository(BaseRepository[Trigger]):
    model = Trigger

    async def get_by_user(self, user_id: UUID, limit: int = 10) -> list[Trigger]:
        """Get top triggers for a user, sorted by frequency."""
        result = await self.db.execute(
            select(Trigger)
            .where(Trigger.user_id == user_id)
            .order_by(Trigger.frequency.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_matching_pattern(self, user_id: UUID, pattern: dict) -> Trigger | None:
        """Find an existing trigger with a matching pattern."""
        result = await self.db.execute(
            select(Trigger).where(
                Trigger.user_id == user_id,
                Trigger.pattern == pattern,
            )
        )
        return result.scalar_one_or_none()
