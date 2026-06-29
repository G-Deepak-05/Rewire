"""
Background task: Trigger pattern analysis.
Runs after journal entries to discover relapse predictors.
"""

import asyncio
from uuid import UUID

from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(name="analyze_triggers", bind=True, max_retries=3)
def analyze_triggers(self, user_id_str: str):
    """Analyze journal entries for trigger patterns."""
    try:
        asyncio.run(_run_analysis(user_id_str))
    except Exception as exc:
        logger.error("Trigger analysis failed", user_id=user_id_str, error=str(exc))
        raise self.retry(exc=exc, countdown=60)


async def _run_analysis(user_id_str: str):
    """Async trigger analysis implementation."""
    from app.db.session import AsyncSessionLocal
    from app.services.trigger_service import TriggerService

    user_id = UUID(user_id_str)

    async with AsyncSessionLocal() as db:
        try:
            svc = TriggerService(db)
            results = await svc.analyze_triggers(user_id)
            await db.commit()
            logger.info(
                "Trigger analysis complete",
                user_id=user_id_str,
                patterns_found=len(results),
            )
        except Exception:
            await db.rollback()
            raise
