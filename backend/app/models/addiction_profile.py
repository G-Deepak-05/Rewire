"""
Addiction profile — stores onboarding data and user preferences.
"""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class AddictionProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "addiction_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Demographics
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Recovery configuration
    goals: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    bad_habits: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    good_habits: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Lifestyle
    sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    exercise_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    work_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Recovery style: structured, flexible, intensive, gentle
    recovery_style: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Trigger & relapse context
    triggers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    relapse_history: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    craving_times: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Status
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="addiction_profile")

    def __repr__(self) -> str:
        return f"<AddictionProfile user_id={self.user_id}>"
