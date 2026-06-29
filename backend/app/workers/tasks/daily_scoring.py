"""
Background task: Daily recovery score computation.
"""

import asyncio
from datetime import date
from uuid import UUID

from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(name="compute_daily_scores")
def compute_daily_scores():
    """Compute daily recovery scores for all active users."""
    asyncio.run(_run_daily_scoring())


async def _run_daily_scoring():
    """Compute scores for all active users."""
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.user import User

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User.id).where(User.is_active == True)
            )
            user_ids = [row[0] for row in result.all()]

            for user_id in user_ids:
                try:
                    await _compute_user_score(db, user_id)
                except Exception as e:
                    logger.error(
                        "Failed to compute score for user",
                        user_id=str(user_id),
                        error=str(e),
                    )

            await db.commit()
            logger.info("Daily scoring complete", users_processed=len(user_ids))
        except Exception:
            await db.rollback()
            raise


async def _compute_user_score(db, user_id: UUID):
    """Compute recovery score for a single user."""
    from datetime import UTC, datetime, timedelta

    from app.models.recovery_score import RecoveryScore
    from app.repositories.journal_repository import JournalRepository
    from app.repositories.recovery_score_repository import RecoveryScoreRepository

    today = date.today()
    now = datetime.now(UTC)
    yesterday_start = datetime(today.year, today.month, today.day, tzinfo=UTC) - timedelta(days=1)

    score_repo = RecoveryScoreRepository(db)
    journal_repo = JournalRepository(db)

    # Check if today's score already exists
    existing = await score_repo.get_by_date(user_id, today)
    if existing:
        return

    # Get yesterday's entries
    entries = await journal_repo.get_entries_since(user_id, yesterday_start)

    # Compute component scores
    relapse_count = sum(1 for e in entries if e.entry_type == "relapse")
    victory_count = sum(1 for e in entries if e.entry_type == "victory")
    craving_count = sum(1 for e in entries if e.entry_type == "craving")

    sleep_vals = [e.sleep_hours_last_night for e in entries if e.sleep_hours_last_night]
    avg_sleep = sum(sleep_vals) / len(sleep_vals) if sleep_vals else 7.0

    stress_vals = [e.stress_level for e in entries if e.stress_level]
    avg_stress = sum(stress_vals) / len(stress_vals) if stress_vals else 5

    # Score calculations (0-100)
    sleep_score = min(100, int((avg_sleep / 8.0) * 100))
    relapse_score = max(0, 100 - (relapse_count * 30))
    consistency_score = min(100, len(entries) * 20)  # Reward journaling

    # Overall = weighted average
    overall = int(
        sleep_score * 0.2
        + relapse_score * 0.35
        + consistency_score * 0.2
        + max(0, (10 - avg_stress) * 10) * 0.15
        + min(100, victory_count * 25) * 0.1
    )

    # Streak
    yesterday_score = await score_repo.get_by_date(user_id, today - timedelta(days=1))
    prev_streak = yesterday_score.streak_days if yesterday_score else 0
    streak = prev_streak + 1 if relapse_count == 0 else 0

    await score_repo.create(
        user_id=user_id,
        score_date=today,
        overall_score=overall,
        sleep_score=sleep_score,
        focus_score=max(0, int((10 - avg_stress) * 10)),
        exercise_score=0,  # Will be tracked in Phase 2
        meditation_score=0,
        screen_time_score=50,  # Default until screen time tracking
        relapse_score=relapse_score,
        consistency_score=consistency_score,
        streak_days=streak,
    )

    # Update gamification streak
    try:
        from app.services.gamification_service import GamificationService
        gam_svc = GamificationService(db)
        await gam_svc.update_streak(user_id, increment=(relapse_count == 0))
    except Exception:
        pass
