"""
User & onboarding service.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.repositories.addiction_profile_repository import AddictionProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import OnboardingRequest

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.profile_repo = AddictionProfileRepository(db)

    async def get_onboarding_status(self, user_id: UUID) -> dict:
        """Check onboarding completion status."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        return {
            "profile_exists": profile is not None,
            "onboarding_completed": profile.onboarding_completed if profile else False,
        }

    async def submit_onboarding(self, user_id: UUID, data: OnboardingRequest):
        """Create or update addiction profile from onboarding data."""
        profile = await self.profile_repo.get_by_user_id(user_id)

        profile_data = data.model_dump(exclude_none=True)
        profile_data["onboarding_completed"] = True

        if profile:
            profile = await self.profile_repo.update(profile, **profile_data)
        else:
            profile = await self.profile_repo.create(user_id=user_id, **profile_data)

        logger.info("Onboarding completed", user_id=str(user_id))

        # Initialize gamification record
        from app.services.gamification_service import GamificationService
        gamification_svc = GamificationService(self.db)
        await gamification_svc.initialize(user_id)

        return profile

    async def update_onboarding(self, user_id: UUID, data: OnboardingRequest):
        """Partially update addiction profile."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Addiction profile")

        update_data = data.model_dump(exclude_none=True)
        return await self.profile_repo.update(profile, **update_data)

    async def get_profile(self, user_id: UUID):
        """Get full addiction profile."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Addiction profile")
        return profile
