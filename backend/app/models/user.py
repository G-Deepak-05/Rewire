"""
User model — authentication and profile.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    # Relationships
    addiction_profile = relationship("AddictionProfile", back_populates="user", uselist=False)
    assessments = relationship("Assessment", back_populates="user", lazy="dynamic")
    journal_entries = relationship("JournalEntry", back_populates="user", lazy="dynamic")
    conversations = relationship("Conversation", back_populates="user", lazy="dynamic")
    triggers = relationship("Trigger", back_populates="user", lazy="dynamic")
    recovery_scores = relationship("RecoveryScore", back_populates="user", lazy="dynamic")
    gamification = relationship(
        "Gamification", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    recovery_plan = relationship(
        "RecoveryPlan", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens = relationship("RefreshToken", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
