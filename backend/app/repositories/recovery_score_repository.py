"""Recovery score repository."""

from datetime import date
from uuid import UUID

from sqlalchemy import select

from app.models.recovery_score import RecoveryScore
from app.repositories.base_repository import BaseRepository


class RecoveryScoreRepository(BaseRepository[RecoveryScore]):
    model = RecoveryScore

    async def get_by_date(self, user_id: UUID, score_date: date) -> RecoveryScore | None:
        result = await self.db.execute(
            select(RecoveryScore).where(
                RecoveryScore.user_id == user_id,
                RecoveryScore.score_date == score_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_history(
        self, user_id: UUID, limit: int = 30
    ) -> list[RecoveryScore]:
        result = await self.db.execute(
            select(RecoveryScore)
            .where(RecoveryScore.user_id == user_id)
            .order_by(RecoveryScore.score_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
