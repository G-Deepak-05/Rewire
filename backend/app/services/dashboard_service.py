"""
Dashboard service — aggregates recovery data for the main dashboard view.
"""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.journal_repository import JournalRepository
from app.repositories.recovery_score_repository import RecoveryScoreRepository
from app.repositories.trigger_repository import TriggerRepository

logger = get_logger(__name__)

# XP thresholds per level
LEVEL_THRESHOLDS = [0, 100, 250, 500, 850, 1300, 1900, 2700, 3700, 5000, 6500, 8500, 11000]


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.journal_repo = JournalRepository(db)
        self.score_repo = RecoveryScoreRepository(db)
        self.trigger_repo = TriggerRepository(db)

    async def get_dashboard(self, user_id: UUID) -> dict:
        """Aggregate all dashboard data."""
        today = date.today()
        now = datetime.now(UTC)
        today_start = datetime(today.year, today.month, today.day, tzinfo=UTC)

        # Recovery score
        today_score = await self.score_repo.get_by_date(user_id, today)
        score_history = await self.score_repo.get_history(user_id, limit=14)

        recovery_score = today_score.overall_score if today_score else 0
        streak_days = today_score.streak_days if today_score else 0

        recovery_trend = [
            {"date": s.score_date.isoformat(), "score": s.overall_score}
            for s in reversed(score_history)
        ]

        # Today's entries
        today_entries = await self.journal_repo.get_entries_since(user_id, today_start)
        cravings_today = sum(1 for e in today_entries if e.entry_type == "craving")
        relapses_today = sum(1 for e in today_entries if e.entry_type == "relapse")
        victories_today = sum(1 for e in today_entries if e.entry_type == "victory")

        # Mood
        mood_today = today_entries[-1].emotion if today_entries else None
        mood_trend = [
            {"date": e.created_at.isoformat(), "emotion": e.emotion, "intensity": e.emotion_intensity}
            for e in today_entries
        ]

        # Risk assessment
        risk = self._compute_risk(today_entries, streak_days, today_score)

        # Top triggers
        triggers = await self.trigger_repo.get_by_user(user_id, limit=5)
        top_triggers = [
            {
                "trigger_type": t.trigger_type,
                "frequency": t.frequency,
                "confidence": t.confidence,
                "insight": t.insight,
            }
            for t in triggers
        ]

        # Gamification
        gamification_data = await self._get_gamification(user_id)

        # AI insight
        daily_insight = await self._generate_daily_insight(user_id, recovery_score, streak_days, triggers)

        return {
            "recovery_score": recovery_score,
            "recovery_trend": recovery_trend,
            "current_risk_level": risk["level"],
            "risk_percentage": risk["percentage"],
            "mood_today": mood_today,
            "mood_trend": mood_trend,
            "streak_days": streak_days,
            "longest_streak": gamification_data.get("longest_streak", 0),
            "cravings_today": cravings_today,
            "relapses_today": relapses_today,
            "victories_today": victories_today,
            "top_triggers": top_triggers,
            "daily_insight": daily_insight,
            "level": gamification_data.get("level", 1),
            "xp": gamification_data.get("xp", 0),
            "xp_to_next_level": gamification_data.get("xp_to_next_level", 100),
            "daily_quests": gamification_data.get("daily_quests", []),
        }

    def _compute_risk(self, today_entries, streak_days, today_score) -> dict:
        """Compute current risk level based on multiple signals."""
        risk_score = 30  # Base risk

        # More cravings today = higher risk
        craving_count = sum(1 for e in today_entries if e.entry_type == "craving")
        risk_score += min(30, craving_count * 10)

        # Relapses today = high risk
        relapse_count = sum(1 for e in today_entries if e.entry_type == "relapse")
        risk_score += min(20, relapse_count * 15)

        # Low streak = higher baseline risk
        if streak_days < 3:
            risk_score += 10

        # High stress today
        stress_vals = [e.stress_level for e in today_entries if e.stress_level]
        if stress_vals and max(stress_vals) >= 8:
            risk_score += 10

        # Poor sleep
        sleep_vals = [e.sleep_hours_last_night for e in today_entries if e.sleep_hours_last_night]
        if sleep_vals and min(sleep_vals) < 5:
            risk_score += 10

        # Cap at 100
        risk_score = min(100, risk_score)

        # Reduce by streak bonus
        if streak_days >= 7:
            risk_score = max(10, risk_score - 15)
        elif streak_days >= 30:
            risk_score = max(5, risk_score - 25)

        # Determine level
        if risk_score < 25:
            level = "low"
        elif risk_score < 50:
            level = "moderate"
        elif risk_score < 75:
            level = "high"
        else:
            level = "critical"

        return {"level": level, "percentage": risk_score}

    async def _get_gamification(self, user_id: UUID) -> dict:
        """Fetch gamification data."""
        try:
            from app.repositories.base_repository import BaseRepository
            from app.models.gamification import Gamification
            from sqlalchemy import select

            result = await self.db.execute(
                select(Gamification).where(Gamification.user_id == user_id)
            )
            gam = result.scalar_one_or_none()
            if gam:
                level = gam.level
                xp = gam.xp
                next_threshold = LEVEL_THRESHOLDS[min(level, len(LEVEL_THRESHOLDS) - 1)]
                return {
                    "level": level,
                    "xp": xp,
                    "xp_to_next_level": max(0, next_threshold - xp),
                    "longest_streak": gam.longest_streak,
                    "daily_quests": gam.daily_quests or [],
                }
        except Exception:
            pass
        return {"level": 1, "xp": 0, "xp_to_next_level": 100, "longest_streak": 0, "daily_quests": []}

    async def _generate_daily_insight(
        self, user_id: UUID, score: int, streak: int, triggers: list
    ) -> str | None:
        """Generate a daily AI insight."""
        try:
            from app.ai.llm import get_llm_response

            trigger_info = ", ".join(t.trigger_type for t in triggers[:3]) if triggers else "none identified yet"
            prompt = f"""Generate a single, actionable daily insight for an addiction recovery user.
Recovery score: {score}/100, Streak: {streak} days, Top triggers: {trigger_info}.
Keep it under 2 sentences. Be specific and motivating, not generic."""

            return await get_llm_response(prompt)
        except Exception:
            if streak >= 7:
                return f"🔥 {streak}-day streak! Your consistency is building new neural pathways."
            elif score >= 70:
                return "Your recovery score is strong today. Keep the momentum going."
            else:
                return "Every small win compounds. Focus on your next 2 hours, not the whole day."

    async def get_score_history(self, user_id: UUID, limit: int = 30) -> dict:
        """Get recovery score history."""
        scores = await self.score_repo.get_history(user_id, limit)
        return {
            "scores": [
                {
                    "date": s.score_date.isoformat(),
                    "overall": s.overall_score,
                    "sleep": s.sleep_score,
                    "focus": s.focus_score,
                    "exercise": s.exercise_score,
                    "relapse": s.relapse_score,
                    "consistency": s.consistency_score,
                    "streak": s.streak_days,
                }
                for s in reversed(scores)
            ],
            "total": len(scores),
        }

    async def get_insights(self, user_id: UUID) -> dict:
        """Generate multiple AI insights based on user data."""
        try:
            from app.ai.llm import get_llm_response

            entries = await self.journal_repo.get_recent(user_id, limit=30)
            triggers = await self.trigger_repo.get_by_user(user_id, limit=5)

            emotion_counts = {}
            for e in entries:
                emotion_counts[e.emotion] = emotion_counts.get(e.emotion, 0) + 1

            trigger_info = [t.insight for t in triggers if t.insight]

            prompt = f"""Based on this addiction recovery data, generate 4-5 specific, data-driven insights.

Journal entries analyzed: {len(entries)}
Emotion breakdown: {emotion_counts}
Known trigger patterns: {trigger_info}

Format each insight as a single sentence starting with a specific observation.
Examples of good insights:
- "You relapse 3x more often after sleeping under 6 hours."
- "Your strongest recovery days are Tuesdays and Wednesdays."
- "Instagram is present in 67% of your craving entries."

Be specific with numbers. Don't be generic."""

            response = await get_llm_response(prompt)
            insights = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
            return {"insights": insights, "generated_at": datetime.now(UTC)}

        except Exception:
            return {
                "insights": [
                    "Keep logging journal entries — patterns become clearer after 10+ entries.",
                    "Users who check in daily recover 40% faster.",
                ],
                "generated_at": datetime.now(UTC),
            }
