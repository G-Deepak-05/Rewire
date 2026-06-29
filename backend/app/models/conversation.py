"""
Conversation model — AI coach chat history.
"""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Auto-generated title from first message
    title: Mapped[str] = mapped_column(String(200), default="New Conversation", nullable=False)

    # Chat messages: [{role: "user"|"assistant", content: str, timestamp: str}]
    messages: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Snapshot of user state at conversation time (for context)
    context_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")

    def __repr__(self) -> str:
        return f"<Conversation {self.title}>"
