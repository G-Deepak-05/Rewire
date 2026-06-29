"""
Journal schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JournalCreateRequest(BaseModel):
    entry_type: str = Field("craving", max_length=20)
    emotion: str = Field("neutral", max_length=30)
    emotion_intensity: int = Field(5, ge=1, le=10)
    location: str | None = Field(None, max_length=50)
    time_of_day: str | None = Field(None, max_length=20)
    people_context: str | None = Field(None, max_length=30)
    energy_level: int | None = Field(None, ge=1, le=10)
    stress_level: int | None = Field(None, ge=1, le=10)
    sleep_hours_last_night: float | None = Field(None, ge=0, le=24)
    device: str | None = Field(None, max_length=20)
    trigger_app: str | None = Field(None, max_length=50)
    notes: str | None = None
    weather: str | None = Field(None, max_length=30)


class JournalEntryResponse(BaseModel):
    id: UUID
    entry_type: str
    emotion: str
    emotion_intensity: int
    location: str | None
    time_of_day: str | None
    people_context: str | None
    energy_level: int | None
    stress_level: int | None
    sleep_hours_last_night: float | None
    device: str | None
    trigger_app: str | None
    notes: str | None
    ai_response: str | None
    weather: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JournalListResponse(BaseModel):
    entries: list[JournalEntryResponse]
    total: int


class JournalStatsResponse(BaseModel):
    total_entries: int
    entries_this_week: int
    most_common_emotion: str | None
    most_common_trigger_app: str | None
    average_stress: float | None
    average_energy: float | None
    relapse_count_this_week: int
    victory_count_this_week: int
    emotion_breakdown: dict  # {"anxious": 5, "bored": 3, ...}
    time_of_day_breakdown: dict  # {"night": 8, "evening": 3, ...}
