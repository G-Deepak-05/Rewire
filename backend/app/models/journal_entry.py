"""
Journal entry model — context-rich craving/relapse/victory tracking.
Instead of just "I relapsed", captures the full environmental context.
"""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class JournalEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "journal_entries"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Entry classification
    entry_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="craving"
    )  # craving, relapse, victory, reflection, check_in

    # Emotional state
    emotion: Mapped[str] = mapped_column(
        String(30), nullable=False, default="neutral"
    )  # anxious, bored, lonely, stressed, angry, sad, happy, neutral, excited, overwhelmed
    emotion_intensity: Mapped[int] = mapped_column(Integer, default=5)  # 1-10

    # Context
    location: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # home, office, commute, gym, outside, friend_house
    time_of_day: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # morning, afternoon, evening, night, late_night
    people_context: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # alone, with_family, with_friends, at_work, in_public

    # Physical state
    energy_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    sleep_hours_last_night: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Digital context
    device: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # phone, laptop, tablet, desktop
    trigger_app: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Instagram, YouTube, TikTok, Reddit, etc.

    # Free-form notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI response to this entry
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional metadata
    weather: Mapped[str | None] = mapped_column(String(30), nullable=True)
    metadata_extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="journal_entries")

    def __repr__(self) -> str:
        return f"<JournalEntry {self.entry_type} emotion={self.emotion}>"
