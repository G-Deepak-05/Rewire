"""
Gamification model — XP, levels, streaks, badges, quests.
"""

import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Gamification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gamification"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Core progression
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)

    # Streaks
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Badges: [{"id": "first_journal", "name": "First Steps", "earned_at": "..."}]
    badges: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Daily quests: [{"id": "...", "title": "...", "completed": false, "xp": 50}]
    daily_quests: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Achievements: [{"id": "...", "name": "...", "progress": 0.5, "target": 1.0}]
    achievements: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Visual progression
    recovery_tree_stage: Mapped[int] = mapped_column(Integer, default=0)
    discipline_score: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="gamification")

    def __repr__(self) -> str:
        return f"<Gamification level={self.level} xp={self.xp}>"
