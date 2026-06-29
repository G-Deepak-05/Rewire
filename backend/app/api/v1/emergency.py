"""
Emergency mode endpoint — crisis intervention.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.core.logging import get_logger
from app.services.journal_service import JournalService
from app.schemas.journal import JournalCreateRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/activate")
async def activate_emergency_mode(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate emergency mode — user is about to relapse.
    Returns immediate AI response, coping tools, and logs the crisis.
    """
    user_id = current_user.id

    # Log this as a journal entry
    journal_svc = JournalService(db)
    entry = await journal_svc.create_entry(
        user_id,
        JournalCreateRequest(
            entry_type="craving",
            emotion="overwhelmed",
            emotion_intensity=9,
            notes="[EMERGENCY MODE ACTIVATED]",
        ),
    )

    # Get AI emergency response
    ai_response = await _get_emergency_response(user_id, db)

    # Award XP for using emergency mode instead of relapsing
    try:
        from app.services.gamification_service import GamificationService
        gam_svc = GamificationService(db)
        await gam_svc.award_xp(user_id, 75, "emergency_survived")
    except Exception:
        pass

    logger.info("Emergency mode activated", user_id=str(user_id))

    return {
        "status": "emergency_active",
        "ai_response": ai_response,
        "coping_tools": {
            "breathing_exercise": {
                "name": "4-7-8 Breathing",
                "steps": [
                    "Inhale through your nose for 4 seconds",
                    "Hold your breath for 7 seconds",
                    "Exhale slowly through your mouth for 8 seconds",
                    "Repeat 4 times",
                ],
                "duration_seconds": 76,
            },
            "grounding_exercise": {
                "name": "5-4-3-2-1 Grounding",
                "steps": [
                    "Name 5 things you can SEE",
                    "Name 4 things you can TOUCH",
                    "Name 3 things you can HEAR",
                    "Name 2 things you can SMELL",
                    "Name 1 thing you can TASTE",
                ],
            },
            "cold_exposure": {
                "name": "Cold Water Reset",
                "instruction": "Run cold water on your wrists for 30 seconds, or splash cold water on your face.",
                "timer_seconds": 30,
            },
            "physical_movement": {
                "name": "Movement Break",
                "options": [
                    "Do 20 pushups",
                    "Run up and down stairs 3 times",
                    "Do 30 jumping jacks",
                    "Walk outside for 5 minutes",
                ],
            },
            "distraction_activities": [
                "Call or text a friend",
                "Start a 5-minute sketch",
                "Listen to your favorite upbeat song",
                "Write down 3 things you're grateful for",
                "Solve a quick puzzle or play a word game",
            ],
        },
        "reminder": "This craving WILL pass. They typically peak at 15-20 minutes then fade. You're stronger than this moment.",
    }


async def _get_emergency_response(user_id, db) -> str:
    """Generate emergency AI response."""
    try:
        from app.ai.llm import get_llm_response
        from app.ai.prompts.coach_system import EMERGENCY_SYSTEM_PROMPT

        # Build minimal context
        context = "User activated emergency mode — experiencing intense craving right now."

        prompt = EMERGENCY_SYSTEM_PROMPT.format(user_context=context)

        return await get_llm_response(
            prompt + "\n\nRespond NOW with immediate crisis intervention steps.",
        )
    except Exception as e:
        logger.warning("Emergency AI response failed", error=str(e))
        return (
            "🛑 STOP. Take a breath. Here's what to do RIGHT NOW:\n\n"
            "1. Stand up and move to a different room\n"
            "2. Splash cold water on your face\n"
            "3. Do 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s (repeat 3x)\n"
            "4. Text or call someone — anyone\n\n"
            "This feeling will pass in 15-20 minutes. You reached out — that's already a win."
        )
