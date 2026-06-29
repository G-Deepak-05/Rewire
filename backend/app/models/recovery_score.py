"""
Recovery score — daily computed wellness & recovery metrics.
"""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class RecoveryScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recovery_scores"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Overall composite score (0-100)
    overall_score: Mapped[int] = mapped_column(Integer, default=0)

    # Component scores (each 0-100)
    sleep_score: Mapped[int] = mapped_column(Integer, default=0)
    focus_score: Mapped[int] = mapped_column(Integer, default=0)
    exercise_score: Mapped[int] = mapped_column(Integer, default=0)
    meditation_score: Mapped[int] = mapped_column(Integer, default=0)
    screen_time_score: Mapped[int] = mapped_column(Integer, default=0)
    relapse_score: Mapped[int] = mapped_column(Integer, default=100)  # starts at 100, decreases on relapse
    consistency_score: Mapped[int] = mapped_column(Integer, default=0)

    # Streaks
    streak_days: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="recovery_scores")

    def __repr__(self) -> str:
        return f"<RecoveryScore {self.score_date} overall={self.overall_score}>"
