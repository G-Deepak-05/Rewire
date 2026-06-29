"""
Assessment model — addiction scoring and risk evaluation.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Assessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # What addiction is being assessed
    addiction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # e.g., porn, social_media, gaming, alcohol, nicotine, food, shopping, gambling, phone

    # Question-answer pairs
    responses: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Computed scores
    addiction_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    risk_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    recovery_difficulty: Mapped[str] = mapped_column(
        String(20), default="moderate"
    )  # low, moderate, high, severe

    # AI-generated analysis
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # When the assessment was completed
    assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="assessments")

    def __repr__(self) -> str:
        return f"<Assessment {self.addiction_type} score={self.addiction_score}>"
