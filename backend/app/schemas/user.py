"""
User & onboarding schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ─── User ─────────────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str | None
    avatar_url: str | None
    is_active: bool
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Onboarding ──────────────────────────────────────────────────────────────
class OnboardingRequest(BaseModel):
    age: int | None = Field(None, ge=13, le=120)
    gender: str | None = Field(None, max_length=20)
    occupation: str | None = Field(None, max_length=100)
    goals: list[str] | None = None
    bad_habits: list[dict] | None = None  # [{"name": "doom_scrolling", "severity": 8}]
    good_habits: list[str] | None = None
    sleep_hours: float | None = Field(None, ge=0, le=24)
    exercise_frequency: str | None = None  # never, rarely, weekly, daily
    stress_level: int | None = Field(None, ge=1, le=10)
    work_hours: float | None = Field(None, ge=0, le=24)
    recovery_style: str | None = None  # structured, flexible, intensive, gentle
    triggers: list[str] | None = None
    relapse_history: dict | None = None
    craving_times: list[str] | None = None  # morning, afternoon, evening, night, late_night


class OnboardingResponse(BaseModel):
    id: UUID
    user_id: UUID
    onboarding_completed: bool
    age: int | None
    gender: str | None
    occupation: str | None
    goals: list | None
    bad_habits: list | None
    good_habits: list | None
    sleep_hours: float | None
    stress_level: int | None
    recovery_style: str | None
    triggers: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OnboardingStatusResponse(BaseModel):
    onboarding_completed: bool
    profile_exists: bool
