"""
Gamification schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GamificationResponse(BaseModel):
    xp: int
    level: int
    streak_days: int
    longest_streak: int
    badges: list[dict]
    daily_quests: list[dict]
    achievements: list[dict]
    recovery_tree_stage: int
    discipline_score: int
    xp_to_next_level: int

    model_config = {"from_attributes": True}


class BadgeResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    earned_at: datetime | None


class QuestCompleteRequest(BaseModel):
    quest_id: str


class XPGainResponse(BaseModel):
    xp_gained: int
    total_xp: int
    level: int
    leveled_up: bool
    new_badges: list[dict]
