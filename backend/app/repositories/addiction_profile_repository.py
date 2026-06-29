"""Addiction profile repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.addiction_profile import AddictionProfile
from app.repositories.base_repository import BaseRepository


class AddictionProfileRepository(BaseRepository[AddictionProfile]):
    model = AddictionProfile

    async def get_by_user_id(self, user_id: UUID) -> AddictionProfile | None:
        result = await self.db.execute(
            select(AddictionProfile).where(AddictionProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
