"""
Journal service — context-rich entry creation with AI responses and trigger analysis.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.journal_repository import JournalRepository
from app.schemas.journal import JournalCreateRequest

logger = get_logger(__name__)


class JournalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = JournalRepository(db)

    async def create_entry(self, user_id: UUID, data: JournalCreateRequest):
        """Create a context-rich journal entry and generate AI response."""
        entry = await self.repo.create(
            user_id=user_id,
            **data.model_dump(exclude_none=True),
        )

        # Generate AI response based on entry context
        ai_response = await self._generate_ai_response(user_id, entry)
        if ai_response:
            entry = await self.repo.update(entry, ai_response=ai_response)

        # Trigger background analysis
        await self._queue_trigger_analysis(user_id)

        # Award XP for journaling
        try:
            from app.services.gamification_service import GamificationService
            gam_svc = GamificationService(self.db)
            await gam_svc.award_xp(user_id, 25, "journal_entry")
        except Exception as e:
            logger.warning("Failed to award XP", error=str(e))

        logger.info(
            "Journal entry created",
            user_id=str(user_id),
            entry_type=data.entry_type,
            emotion=data.emotion,
        )

        return entry

    async def get_entries(self, user_id: UUID, offset: int = 0, limit: int = 20):
        """Get paginated journal entries."""
        entries, total = await self.repo.get_multi(
            filters=[self.repo.model.user_id == user_id],
            offset=offset,
            limit=limit,
        )
        return {"entries": entries, "total": total}

    async def get_entry(self, user_id: UUID, entry_id: UUID):
        """Get a single journal entry."""
        from app.core.exceptions import NotFoundError
        entry = await self.repo.get(entry_id)
        if not entry or entry.user_id != user_id:
            raise NotFoundError("Journal entry", str(entry_id))
        return entry

    async def get_stats(self, user_id: UUID) -> dict:
        """Compute journal statistics for the last 7 days."""
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)

        entries_this_week = await self.repo.get_entries_since(user_id, week_ago)
        all_entries_count = await self.repo.count(self.repo.model.user_id == user_id)
        emotion_breakdown = await self.repo.get_emotion_breakdown(user_id)
        time_breakdown = await self.repo.get_time_of_day_breakdown(user_id)

        relapse_count = await self.repo.count_by_type_since(user_id, "relapse", week_ago)
        victory_count = await self.repo.count_by_type_since(user_id, "victory", week_ago)

        # Compute averages
        stress_vals = [e.stress_level for e in entries_this_week if e.stress_level]
        energy_vals = [e.energy_level for e in entries_this_week if e.energy_level]

        most_common_emotion = max(emotion_breakdown, key=emotion_breakdown.get) if emotion_breakdown else None
        trigger_apps = [e.trigger_app for e in entries_this_week if e.trigger_app]
        most_common_app = max(set(trigger_apps), key=trigger_apps.count) if trigger_apps else None

        return {
            "total_entries": all_entries_count,
            "entries_this_week": len(entries_this_week),
            "most_common_emotion": most_common_emotion,
            "most_common_trigger_app": most_common_app,
            "average_stress": round(sum(stress_vals) / len(stress_vals), 1) if stress_vals else None,
            "average_energy": round(sum(energy_vals) / len(energy_vals), 1) if energy_vals else None,
            "relapse_count_this_week": relapse_count,
            "victory_count_this_week": victory_count,
            "emotion_breakdown": emotion_breakdown,
            "time_of_day_breakdown": time_breakdown,
        }

    async def _generate_ai_response(self, user_id: UUID, entry) -> str | None:
        """Generate a contextual AI response to the journal entry."""
        try:
            from app.ai.llm import get_llm_response

            context_parts = [
                f"Entry type: {entry.entry_type}",
                f"Emotion: {entry.emotion} (intensity: {entry.emotion_intensity}/10)",
            ]
            if entry.location:
                context_parts.append(f"Location: {entry.location}")
            if entry.time_of_day:
                context_parts.append(f"Time: {entry.time_of_day}")
            if entry.people_context:
                context_parts.append(f"Social context: {entry.people_context}")
            if entry.stress_level:
                context_parts.append(f"Stress: {entry.stress_level}/10")
            if entry.energy_level:
                context_parts.append(f"Energy: {entry.energy_level}/10")
            if entry.sleep_hours_last_night:
                context_parts.append(f"Sleep last night: {entry.sleep_hours_last_night}h")
            if entry.trigger_app:
                context_parts.append(f"Trigger app: {entry.trigger_app}")
            if entry.notes:
                context_parts.append(f"Notes: {entry.notes}")

            context = "\n".join(context_parts)

            prompt = f"""You are Rewire, an empathetic AI recovery coach. A user just logged a journal entry:

{context}

Respond in 2-3 sentences. Rules:
- Do NOT lecture or moralize
- If it's a craving: acknowledge it, ask what they need right now, suggest ONE specific action
- If it's a relapse: no judgment, focus on what they can learn, remind them streaks don't define recovery
- If it's a victory: genuinely celebrate, reinforce the behavior
- If it's a reflection: validate their self-awareness, ask a gentle follow-up question
- Match the emotional tone — if they're struggling, be warm. If they're proud, be excited."""

            return await get_llm_response(prompt)
        except Exception as e:
            logger.warning("AI response failed for journal entry", error=str(e))
            return None

    async def _queue_trigger_analysis(self, user_id: UUID) -> None:
        """Queue background trigger pattern analysis (Celery task)."""
        try:
            from app.workers.tasks.trigger_analysis import analyze_triggers
            analyze_triggers.delay(str(user_id))
        except Exception as e:
            logger.warning("Failed to queue trigger analysis", error=str(e))
