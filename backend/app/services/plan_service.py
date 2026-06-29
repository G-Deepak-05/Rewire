import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.recovery_plan import RecoveryPlan
from app.models.addiction_profile import AddictionProfile
from app.ai.llm import get_llm_response
from app.ai.prompts.coach_system import COACH_SYSTEM_PROMPT

logger = get_logger(__name__)


class PlanService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_plan(self, user_id: UUID) -> dict | None:
        result = await self.db.execute(select(RecoveryPlan).where(RecoveryPlan.user_id == user_id))
        plan = result.scalar_one_or_none()
        if not plan:
            return None
            
        return {
            "phases": plan.phases,
            "current_phase_index": plan.current_phase_index,
            "current_day": plan.current_day,
            "completed_tasks": plan.completed_tasks,
            "is_active": plan.is_active,
        }

    async def generate_plan(self, user_id: UUID) -> RecoveryPlan:
        # Get profile
        result = await self.db.execute(select(AddictionProfile).where(AddictionProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError("Profile not found")

        # Prepare context for AI
        context = f"""
        User Profile:
        Target Addiction: {profile.bad_habits[0]['name'] if profile.bad_habits else 'Unknown'} (Severity: {profile.bad_habits[0]['severity'] if profile.bad_habits else 'Unknown'}/10)
        Goal: {profile.goals[0] if profile.goals else 'Unknown'}
        Triggers: {profile.triggers}
        Sleep: {profile.sleep_hours} hours
        Stress Level: {profile.stress_level}/10
        Desired Good Habits: {profile.good_habits}
        """

        prompt = f"""
        {COACH_SYSTEM_PROMPT}
        
        Based on the User Profile below, generate a 4-phase structured recovery program (30 days total).
        
        {context}
        
        Respond ONLY with a valid JSON array. Do not include markdown formatting like ```json.
        Example format:
        [
            {{
                "phase": 1,
                "title": "Awareness & Detox",
                "duration_days": 7,
                "daily_tasks": ["Identify triggers", "Drink 2L water", "Sleep 8 hours"]
            }},
            {{
                "phase": 2,
                "title": "Building New Habits",
                "duration_days": 7,
                "daily_tasks": ["10 min Meditation", "Read 10 pages"]
            }}
        ]
        """

        try:
            response_text = await get_llm_response(prompt)
            # Clean up potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            phases = json.loads(response_text.strip())
        except Exception as e:
            logger.error("Failed to generate plan via AI, using fallback.", error=str(e))
            phases = [
                {
                    "phase": 1,
                    "title": "Awareness & Detox",
                    "duration_days": 7,
                    "daily_tasks": ["Identify triggers", "Journal daily", "Drink water"]
                },
                {
                    "phase": 2,
                    "title": "Building Replacements",
                    "duration_days": 7,
                    "daily_tasks": ["Exercise for 20 mins", "Meditate for 5 mins"]
                },
                {
                    "phase": 3,
                    "title": "Strengthening Resistance",
                    "duration_days": 7,
                    "daily_tasks": ["Social connection", "Review goals"]
                },
                {
                    "phase": 4,
                    "title": "Long-term Maintenance",
                    "duration_days": 9,
                    "daily_tasks": ["Help others", "Reflect on journey"]
                }
            ]

        # Save to DB
        plan = RecoveryPlan(
            user_id=user_id,
            phases=phases,
            current_phase_index=0,
            current_day=1,
            completed_tasks={},
            is_active=True
        )
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan

    async def toggle_task(self, user_id: UUID, day: int, task: str) -> dict:
        result = await self.db.execute(select(RecoveryPlan).where(RecoveryPlan.user_id == user_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundError("Recovery plan")

        day_key = f"day_{day}"
        tasks = dict(plan.completed_tasks)
        
        if day_key not in tasks:
            tasks[day_key] = []
            
        if task in tasks[day_key]:
            tasks[day_key].remove(task)
        else:
            tasks[day_key].append(task)
            
        plan.completed_tasks = tasks
        await self.db.commit()
        
        return {"completed_tasks": tasks}
