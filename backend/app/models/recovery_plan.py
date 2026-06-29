"""
Recovery Plan model — AI-generated structured training program.
"""

import uuid
from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class RecoveryPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recovery_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # The AI-generated plan structure
    # e.g. [{"phase": 1, "title": "Awareness", "duration_days": 7, "daily_tasks": ["Meditation", "Journaling"]}]
    phases: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Current progress
    current_phase_index: Mapped[int] = mapped_column(Integer, default=0)
    current_day: Mapped[int] = mapped_column(Integer, default=1)

    # Tracking completed tasks per day: {"day_1": ["Meditation"], "day_2": []}
    completed_tasks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="recovery_plan")

    def __repr__(self) -> str:
        return f"<RecoveryPlan user_id={self.user_id}>"
