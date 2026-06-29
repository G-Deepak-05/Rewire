"""Journal entry repository."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from app.models.journal_entry import JournalEntry
from app.repositories.base_repository import BaseRepository


class JournalRepository(BaseRepository[JournalEntry]):
    model = JournalEntry

    async def get_recent(self, user_id: UUID, limit: int = 30) -> list[JournalEntry]:
        """Get the N most recent journal entries for a user."""
        result = await self.db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_entries_since(
        self, user_id: UUID, since: datetime
    ) -> list[JournalEntry]:
        """Get entries created after a specific timestamp."""
        result = await self.db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id, JournalEntry.created_at >= since)
            .order_by(JournalEntry.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_type_since(
        self, user_id: UUID, entry_type: str, since: datetime
    ) -> int:
        """Count entries of a specific type since a timestamp."""
        return await self.count(
            JournalEntry.user_id == user_id,
            JournalEntry.entry_type == entry_type,
            JournalEntry.created_at >= since,
        )

    async def get_emotion_breakdown(self, user_id: UUID, days: int = 7) -> dict[str, int]:
        """Get emotion frequency breakdown for the last N days."""
        since = datetime.now(UTC) - timedelta(days=days)
        result = await self.db.execute(
            select(JournalEntry.emotion, func.count())
            .where(JournalEntry.user_id == user_id, JournalEntry.created_at >= since)
            .group_by(JournalEntry.emotion)
        )
        return dict(result.all())

    async def get_time_of_day_breakdown(self, user_id: UUID, days: int = 7) -> dict[str, int]:
        """Get time-of-day frequency breakdown."""
        since = datetime.now(UTC) - timedelta(days=days)
        result = await self.db.execute(
            select(JournalEntry.time_of_day, func.count())
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.created_at >= since,
                JournalEntry.time_of_day.isnot(None),
            )
            .group_by(JournalEntry.time_of_day)
        )
        return dict(result.all())
