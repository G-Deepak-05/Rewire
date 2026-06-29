"""
Dashboard schemas.
"""

from datetime import date, datetime

from pydantic import BaseModel


class TriggerSummary(BaseModel):
    trigger_type: str
    frequency: int
    confidence: float
    insight: str | None


class DashboardResponse(BaseModel):
    # Recovery score
    recovery_score: int
    recovery_trend: list[dict]  # [{"date": "2024-01-01", "score": 75}]

    # Risk
    current_risk_level: str  # low, moderate, high, critical
    risk_percentage: int

    # Mood & wellness
    mood_today: str | None
    mood_trend: list[dict]

    # Streaks
    streak_days: int
    longest_streak: int

    # Cravings today
    cravings_today: int
    relapses_today: int
    victories_today: int

    # Top triggers
    top_triggers: list[TriggerSummary]

    # AI insight
    daily_insight: str | None

    # Gamification
    level: int
    xp: int
    xp_to_next_level: int
    daily_quests: list[dict]


class RecoveryScoreHistoryResponse(BaseModel):
    scores: list[dict]  # [{"date": "...", "overall": 75, "sleep": 80, ...}]
    total: int


class InsightsResponse(BaseModel):
    insights: list[str]
    generated_at: datetime
