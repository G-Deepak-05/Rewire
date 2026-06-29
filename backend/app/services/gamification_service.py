"""
Gamification service — XP, levels, streaks, badges, daily quests.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.gamification import Gamification

logger = get_logger(__name__)

# Level thresholds
LEVEL_THRESHOLDS = [0, 100, 250, 500, 850, 1300, 1900, 2700, 3700, 5000, 6500, 8500, 11000]

# Badge definitions
BADGE_DEFINITIONS = {
    "first_journal": {"name": "First Steps", "description": "Logged your first journal entry", "icon": "📝"},
    "streak_7": {"name": "Week Warrior", "description": "7-day streak", "icon": "🔥"},
    "streak_30": {"name": "Monthly Master", "description": "30-day streak", "icon": "💪"},
    "streak_90": {"name": "Quarter Champion", "description": "90-day streak", "icon": "🏆"},
    "journal_10": {"name": "Self-Aware", "description": "10 journal entries", "icon": "🧠"},
    "journal_50": {"name": "Deep Thinker", "description": "50 journal entries", "icon": "📚"},
    "coach_chat": {"name": "Seeking Help", "description": "First AI coaching session", "icon": "💬"},
    "emergency_survived": {"name": "Crisis Survivor", "description": "Used emergency mode and stayed strong", "icon": "🛡️"},
    "assessment_complete": {"name": "Know Thyself", "description": "Completed an addiction assessment", "icon": "🔍"},
    "level_5": {"name": "Rising Phoenix", "description": "Reached level 5", "icon": "🌅"},
    "level_10": {"name": "Transformation", "description": "Reached level 10", "icon": "⚡"},
}

# XP awards
XP_REWARDS = {
    "journal_entry": 25,
    "coaching_session": 15,
    "daily_checkin": 30,
    "assessment_complete": 50,
    "quest_complete": 40,
    "emergency_survived": 75,
    "streak_milestone": 100,
    "victory_logged": 35,
}


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self, user_id: UUID) -> Gamification:
        """Create initial gamification record for a new user."""
        existing = await self._get_gamification(user_id)
        if existing:
            return existing

        gam = Gamification(
            user_id=user_id,
            xp=0,
            level=1,
            streak_days=0,
            longest_streak=0,
            badges=[],
            daily_quests=self._generate_daily_quests(),
            achievements=[],
            recovery_tree_stage=0,
            discipline_score=0,
        )
        self.db.add(gam)
        await self.db.flush()
        await self.db.refresh(gam)
        return gam

    async def award_xp(self, user_id: UUID, amount: int, reason: str) -> dict:
        """Award XP and handle level ups."""
        gam = await self._get_gamification(user_id)
        if not gam:
            gam = await self.initialize(user_id)

        old_level = gam.level
        gam.xp += amount

        # Check level up
        new_level = self._compute_level(gam.xp)
        leveled_up = new_level > old_level
        gam.level = new_level

        # Check for new badges
        new_badges = await self._check_badges(user_id, gam, reason)

        self.db.add(gam)
        await self.db.flush()

        if leveled_up:
            logger.info("User leveled up", user_id=str(user_id), level=new_level)

        return {
            "xp_gained": amount,
            "total_xp": gam.xp,
            "level": gam.level,
            "leveled_up": leveled_up,
            "new_badges": new_badges,
        }

    async def update_streak(self, user_id: UUID, increment: bool = True) -> dict:
        """Update daily streak."""
        gam = await self._get_gamification(user_id)
        if not gam:
            gam = await self.initialize(user_id)

        if increment:
            gam.streak_days += 1
            if gam.streak_days > gam.longest_streak:
                gam.longest_streak = gam.streak_days
        else:
            gam.streak_days = 0

        self.db.add(gam)
        await self.db.flush()

        return {"streak_days": gam.streak_days, "longest_streak": gam.longest_streak}

    async def complete_quest(self, user_id: UUID, quest_id: str) -> dict:
        """Complete a daily quest and award XP."""
        gam = await self._get_gamification(user_id)
        if not gam:
            return {"error": "No gamification record"}

        quests = list(gam.daily_quests or [])
        quest_found = False
        for quest in quests:
            if quest.get("id") == quest_id and not quest.get("completed"):
                quest["completed"] = True
                quest_found = True
                break

        if not quest_found:
            return {"error": "Quest not found or already completed"}

        gam.daily_quests = quests
        self.db.add(gam)
        await self.db.flush()

        # Award XP
        return await self.award_xp(user_id, XP_REWARDS["quest_complete"], "quest_complete")

    def _compute_level(self, xp: int) -> int:
        """Compute level from total XP."""
        level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if xp >= threshold:
                level = i + 1
            else:
                break
        return level

    def _generate_daily_quests(self) -> list[dict]:
        """Generate a set of daily quests."""
        return [
            {"id": "journal_checkin", "title": "Log a journal entry", "xp": 25, "completed": False},
            {"id": "drink_water", "title": "Drink 8 glasses of water", "xp": 15, "completed": False},
            {"id": "no_trigger_app", "title": "Avoid trigger apps for 2 hours", "xp": 40, "completed": False},
            {"id": "exercise_10min", "title": "Exercise for 10 minutes", "xp": 30, "completed": False},
            {"id": "gratitude", "title": "Write 3 things you're grateful for", "xp": 20, "completed": False},
        ]

    async def _check_badges(self, user_id: UUID, gam: Gamification, reason: str) -> list[dict]:
        """Check and award eligible badges."""
        current_badges = set(b.get("id") for b in (gam.badges or []))
        new_badges = []

        checks = {
            "first_journal": reason == "journal_entry" and "first_journal" not in current_badges,
            "coach_chat": reason == "coaching_session" and "coach_chat" not in current_badges,
            "assessment_complete": reason == "assessment_complete" and "assessment_complete" not in current_badges,
            "emergency_survived": reason == "emergency_survived" and "emergency_survived" not in current_badges,
            "streak_7": gam.streak_days >= 7 and "streak_7" not in current_badges,
            "streak_30": gam.streak_days >= 30 and "streak_30" not in current_badges,
            "streak_90": gam.streak_days >= 90 and "streak_90" not in current_badges,
            "level_5": gam.level >= 5 and "level_5" not in current_badges,
            "level_10": gam.level >= 10 and "level_10" not in current_badges,
        }

        badges_list = list(gam.badges or [])
        for badge_id, should_award in checks.items():
            if should_award and badge_id in BADGE_DEFINITIONS:
                badge_def = BADGE_DEFINITIONS[badge_id]
                badge_entry = {
                    "id": badge_id,
                    "name": badge_def["name"],
                    "description": badge_def["description"],
                    "icon": badge_def["icon"],
                    "earned_at": datetime.now(UTC).isoformat(),
                }
                badges_list.append(badge_entry)
                new_badges.append(badge_entry)

        if new_badges:
            gam.badges = badges_list

        return new_badges

    async def _get_gamification(self, user_id: UUID) -> Gamification | None:
        """Fetch gamification record for a user."""
        result = await self.db.execute(
            select(Gamification).where(Gamification.user_id == user_id)
        )
        return result.scalar_one_or_none()
