"""
Assessment service — generates questions, computes addiction/risk scores, produces AI analysis.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.repositories.assessment_repository import AssessmentRepository

logger = get_logger(__name__)

# ─── Question Banks ──────────────────────────────────────────────────────────
# Each addiction type has tailored assessment questions
QUESTION_BANKS: dict[str, list[dict]] = {
    "porn": [
        {"id": "frequency", "text": "How often do you watch pornography?", "type": "choice",
         "options": ["Never", "Once a month", "Weekly", "Several times a week", "Daily", "Multiple times daily"],
         "weights": [0, 10, 30, 50, 75, 100]},
        {"id": "urge_intensity", "text": "How intense are your urges on a scale of 1-10?", "type": "scale",
         "min": 1, "max": 10},
        {"id": "time_spent", "text": "How much time per session?", "type": "choice",
         "options": ["Under 15 min", "15-30 min", "30-60 min", "1-2 hours", "2+ hours"],
         "weights": [10, 25, 50, 75, 100]},
        {"id": "impact_life", "text": "Has it affected your relationships, work, or self-esteem?", "type": "choice",
         "options": ["Not at all", "Slightly", "Moderately", "Significantly", "Severely"],
         "weights": [0, 20, 45, 70, 100]},
        {"id": "failed_attempts", "text": "How many times have you tried to quit?", "type": "choice",
         "options": ["Never tried", "1-2 times", "3-5 times", "5-10 times", "10+ times"],
         "weights": [15, 30, 50, 70, 90]},
        {"id": "trigger_emotion", "text": "What emotion most often triggers use?", "type": "choice",
         "options": ["Boredom", "Loneliness", "Stress", "Anxiety", "Sadness", "Habit/Routine"],
         "weights": [40, 60, 55, 65, 70, 50]},
        {"id": "escalation", "text": "Has the content you consume escalated in intensity?", "type": "choice",
         "options": ["No", "Slightly", "Noticeably", "Significantly"],
         "weights": [0, 30, 60, 95]},
    ],
    "social_media": [
        {"id": "daily_hours", "text": "How many hours per day do you spend on social media?", "type": "choice",
         "options": ["Under 1 hour", "1-2 hours", "2-4 hours", "4-6 hours", "6+ hours"],
         "weights": [10, 25, 50, 75, 100]},
        {"id": "first_check", "text": "How soon after waking do you check social media?", "type": "choice",
         "options": ["After morning routine", "Within 30 min", "Within 10 min", "Immediately in bed"],
         "weights": [10, 35, 65, 95]},
        {"id": "doom_scroll", "text": "How often do you lose track of time scrolling?", "type": "choice",
         "options": ["Rarely", "Sometimes", "Often", "Almost always"],
         "weights": [15, 40, 70, 95]},
        {"id": "anxiety_without", "text": "Do you feel anxious without your phone?", "type": "choice",
         "options": ["Not at all", "Slightly", "Moderately", "Very anxious", "Can't function"],
         "weights": [0, 20, 50, 75, 100]},
        {"id": "comparison", "text": "How much does social media affect your self-image?", "type": "scale",
         "min": 1, "max": 10},
        {"id": "sleep_impact", "text": "Does social media affect your sleep?", "type": "choice",
         "options": ["Never", "Occasionally", "Frequently", "Every night"],
         "weights": [0, 30, 65, 95]},
    ],
    "gaming": [
        {"id": "daily_hours", "text": "How many hours per day do you game?", "type": "choice",
         "options": ["Under 1 hour", "1-3 hours", "3-5 hours", "5-8 hours", "8+ hours"],
         "weights": [10, 25, 50, 75, 100]},
        {"id": "skip_activities", "text": "Do you skip meals, sleep, or social activities to game?", "type": "choice",
         "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
         "weights": [0, 20, 45, 70, 100]},
        {"id": "withdrawal", "text": "Do you feel irritable when you can't play?", "type": "choice",
         "options": ["Not at all", "Slightly", "Moderately", "Very much", "Extremely"],
         "weights": [0, 20, 50, 75, 100]},
        {"id": "priority", "text": "Is gaming your top priority over other responsibilities?", "type": "choice",
         "options": ["No", "Sometimes", "Often", "Almost always"],
         "weights": [0, 35, 65, 95]},
        {"id": "spending", "text": "How much do you spend on games monthly?", "type": "choice",
         "options": ["Nothing", "Under $20", "$20-50", "$50-100", "$100+"],
         "weights": [0, 15, 35, 60, 90]},
    ],
}

# Default questions for types not in the bank
DEFAULT_QUESTIONS = [
    {"id": "frequency", "text": "How often do you engage in this behavior?", "type": "choice",
     "options": ["Rarely", "Weekly", "Several times a week", "Daily", "Multiple times daily"],
     "weights": [10, 25, 50, 75, 100]},
    {"id": "urge_intensity", "text": "How intense are your urges? (1-10)", "type": "scale",
     "min": 1, "max": 10},
    {"id": "impact", "text": "How much has this affected your life?", "type": "choice",
     "options": ["Not at all", "Slightly", "Moderately", "Significantly", "Severely"],
     "weights": [0, 20, 45, 70, 100]},
    {"id": "control", "text": "Do you feel in control?", "type": "choice",
     "options": ["Completely", "Mostly", "Somewhat", "Barely", "Not at all"],
     "weights": [0, 20, 45, 70, 100]},
    {"id": "failed_attempts", "text": "How many times have you tried to stop?", "type": "choice",
     "options": ["Never tried", "1-2 times", "3-5 times", "5-10 times", "10+ times"],
     "weights": [15, 30, 50, 70, 90]},
    {"id": "trigger_emotion", "text": "What emotion triggers this behavior most?", "type": "choice",
     "options": ["Boredom", "Loneliness", "Stress", "Anxiety", "Sadness", "Habit"],
     "weights": [40, 60, 55, 65, 70, 50]},
]


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AssessmentRepository(db)

    async def start_assessment(self, user_id: UUID, addiction_type: str) -> dict:
        """Create assessment and return questions."""
        questions = QUESTION_BANKS.get(addiction_type, DEFAULT_QUESTIONS)

        assessment = await self.repo.create(
            user_id=user_id,
            addiction_type=addiction_type,
            responses={},
        )

        return {
            "assessment_id": assessment.id,
            "addiction_type": addiction_type,
            "questions": questions,
        }

    async def submit_assessment(self, user_id: UUID, assessment_id: UUID, responses: dict) -> object:
        """Process responses, compute scores, generate AI analysis."""
        assessment = await self.repo.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            raise NotFoundError("Assessment", str(assessment_id))

        questions = QUESTION_BANKS.get(assessment.addiction_type, DEFAULT_QUESTIONS)

        # Compute addiction score
        addiction_score = self._compute_addiction_score(questions, responses)
        risk_score = self._compute_risk_score(addiction_score, responses)
        recovery_difficulty = self._determine_difficulty(addiction_score)

        # Generate AI analysis
        ai_analysis = await self._generate_analysis(
            assessment.addiction_type, responses, addiction_score, risk_score
        )

        # Update assessment
        assessment = await self.repo.update(
            assessment,
            responses=responses,
            addiction_score=addiction_score,
            risk_score=risk_score,
            recovery_difficulty=recovery_difficulty,
            ai_analysis=ai_analysis,
            assessed_at=datetime.now(UTC),
        )

        return assessment

    def _compute_addiction_score(self, questions: list[dict], responses: dict) -> int:
        """Weighted average of all question scores."""
        total_score = 0
        question_count = 0

        for q in questions:
            answer = responses.get(q["id"])
            if answer is None:
                continue

            if q["type"] == "scale":
                # Normalize scale to 0-100
                min_val = q.get("min", 1)
                max_val = q.get("max", 10)
                total_score += int((int(answer) - min_val) / (max_val - min_val) * 100)
                question_count += 1
            elif q["type"] == "choice" and "weights" in q:
                options = q["options"]
                weights = q["weights"]
                if answer in options:
                    idx = options.index(answer)
                    total_score += weights[idx]
                elif isinstance(answer, int) and 0 <= answer < len(weights):
                    total_score += weights[answer]
                question_count += 1

        return int(total_score / max(question_count, 1))

    def _compute_risk_score(self, addiction_score: int, responses: dict) -> int:
        """Risk score factors in addiction score plus escalation indicators."""
        risk = addiction_score

        # Boost risk for failed quit attempts
        failed = responses.get("failed_attempts")
        if failed and isinstance(failed, str) and "10+" in failed:
            risk = min(100, risk + 15)
        elif failed and isinstance(failed, str) and "5-10" in failed:
            risk = min(100, risk + 10)

        # Boost risk for high urge intensity
        urge = responses.get("urge_intensity")
        if urge and int(urge) >= 8:
            risk = min(100, risk + 10)

        return risk

    def _determine_difficulty(self, score: int) -> str:
        """Map score to recovery difficulty."""
        if score < 25:
            return "low"
        elif score < 50:
            return "moderate"
        elif score < 75:
            return "high"
        return "severe"

    async def _generate_analysis(
        self, addiction_type: str, responses: dict, addiction_score: int, risk_score: int
    ) -> str:
        """Use LLM to generate personalized assessment analysis."""
        try:
            from app.ai.llm import get_llm_response

            prompt = f"""You are an empathetic addiction recovery specialist. Analyze this assessment:

Addiction Type: {addiction_type}
Addiction Score: {addiction_score}/100
Risk Score: {risk_score}/100
Responses: {responses}

Provide a brief, compassionate analysis (3-4 sentences) that:
1. Acknowledges their situation without judgment
2. Identifies their primary challenge
3. Gives one specific, actionable first step
4. Instills hope about recovery

Do NOT lecture. Be direct and warm."""

            return await get_llm_response(prompt)
        except Exception as e:
            logger.warning("AI analysis failed, using fallback", error=str(e))
            return self._fallback_analysis(addiction_score, risk_score)

    def _fallback_analysis(self, addiction_score: int, risk_score: int) -> str:
        if addiction_score < 30:
            return ("Your assessment shows early-stage patterns. This is actually great news — "
                    "catching it early makes recovery much smoother. Start with small, consistent changes.")
        elif addiction_score < 60:
            return ("Your patterns show moderate dependency. The fact that you're here taking this assessment "
                    "shows real strength. Focus on identifying your top 2 triggers and building alternatives.")
        else:
            return ("Your assessment indicates significant dependency, but recovery is absolutely possible. "
                    "Many people in your situation have successfully rewired their habits. "
                    "Start with the emergency tools and daily check-ins.")

    async def get_history(self, user_id: UUID) -> dict:
        """Get assessment history for a user."""
        assessments, total = await self.repo.get_multi(
            filters=[self.repo.model.user_id == user_id],
            limit=50,
        )
        return {"assessments": assessments, "total": total}
