"""Assessment repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.assessment import Assessment
from app.repositories.base_repository import BaseRepository


class AssessmentRepository(BaseRepository[Assessment]):
    model = Assessment

    async def get_by_user_and_type(
        self, user_id: UUID, addiction_type: str
    ) -> list[Assessment]:
        result = await self.db.execute(
            select(Assessment)
            .where(Assessment.user_id == user_id, Assessment.addiction_type == addiction_type)
            .order_by(Assessment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_user(self, user_id: UUID) -> Assessment | None:
        result = await self.db.execute(
            select(Assessment)
            .where(Assessment.user_id == user_id)
            .order_by(Assessment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
