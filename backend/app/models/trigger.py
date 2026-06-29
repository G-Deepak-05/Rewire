"""
Trigger model — AI-discovered patterns that lead to relapse.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Trigger(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "triggers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Human-readable trigger description
    trigger_type: Mapped[str] = mapped_column(
        String(200), nullable=False
    )  # e.g., "loneliness + late_night + phone + Instagram"

    # Structured pattern data
    pattern: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # e.g., {"emotion": "lonely", "time": "late_night", "device": "phone", "app": "Instagram",
    #         "day_of_week": "saturday", "location": "bedroom"}

    # How often this pattern leads to relapse
    frequency: Mapped[int] = mapped_column(Integer, default=1)

    # AI confidence in this pattern (0.0 - 1.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)

    # AI-generated insight
    insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    # e.g., "Every Saturday around 11 PM when you're alone in your bedroom browsing Instagram,
    #         you experience strong cravings."

    # Timestamps
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Trigger {self.trigger_type} freq={self.frequency} conf={self.confidence}>"
