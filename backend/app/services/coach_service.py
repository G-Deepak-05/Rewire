"""
AI Coach service — manages conversations with the LangGraph recovery coach agent.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.repositories.conversation_repository import ConversationRepository

logger = get_logger(__name__)


class CoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ConversationRepository(db)

    async def chat(self, user_id: UUID, message: str, conversation_id: UUID | None = None) -> dict:
        """Send a message to the AI coach and get a response."""
        # Get or create conversation
        if conversation_id:
            conversation = await self.repo.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise NotFoundError("Conversation", str(conversation_id))
        else:
            conversation = await self.repo.create(
                user_id=user_id,
                title="New Conversation",
                messages=[],
            )

        # Add user message
        messages = list(conversation.messages or [])
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Build context for the AI
        context = await self._build_context(user_id)

        # Get AI response
        ai_response = await self._get_ai_response(messages, context)

        # Add AI response
        messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Auto-generate title from first message
        title = conversation.title
        if title == "New Conversation" and len(messages) >= 2:
            title = message[:80] + ("..." if len(message) > 80 else "")

        # Update conversation
        conversation = await self.repo.update(
            conversation,
            messages=messages,
            title=title,
        )

        # Award XP for coaching session
        try:
            from app.services.gamification_service import GamificationService
            gam_svc = GamificationService(self.db)
            await gam_svc.award_xp(user_id, 15, "coaching_session")
        except Exception:
            pass

        return {
            "conversation_id": conversation.id,
            "response": ai_response,
            "conversation_title": title,
        }

    async def stream_chat(self, user_id: UUID, message: str, conversation_id: UUID | None = None):
        """Stream response from the AI coach."""
        # Get or create conversation
        if conversation_id:
            conversation = await self.repo.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise NotFoundError("Conversation", str(conversation_id))
        else:
            conversation = await self.repo.create(
                user_id=user_id,
                title="New Conversation",
                messages=[],
            )

        # Add user message
        messages = list(conversation.messages or [])
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Build context for the AI
        context = await self._build_context(user_id)

        # Yield chunks
        from app.ai.llm import get_llm_streaming_response
        from app.ai.prompts.coach_system import COACH_SYSTEM_PROMPT

        system_prompt = COACH_SYSTEM_PROMPT.format(user_context=context)
        llm_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages[-20:]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        full_response = ""
        try:
            async for chunk in get_llm_streaming_response(llm_messages):
                full_response += chunk
                yield chunk
        except Exception as e:
            logger.error("AI coach streaming failed", error=str(e))
            fallback = self._fallback_response(message)
            full_response = fallback
            yield fallback

        # Add AI response and update DB
        messages.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        title = conversation.title
        if title == "New Conversation" and len(messages) >= 2:
            title = message[:80] + ("..." if len(message) > 80 else "")

        await self.repo.update(
            conversation,
            messages=messages,
            title=title,
        )

        try:
            from app.services.gamification_service import GamificationService
            gam_svc = GamificationService(self.db)
            await gam_svc.award_xp(user_id, 15, "coaching_session")
        except Exception:
            pass

    async def get_conversations(self, user_id: UUID) -> dict:
        """List user conversations."""
        conversations = await self.repo.get_by_user(user_id)

        items = []
        for c in conversations:
            items.append({
                "id": c.id,
                "title": c.title,
                "message_count": len(c.messages or []),
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            })

        return {"conversations": items, "total": len(items)}

    async def get_conversation(self, user_id: UUID, conversation_id: UUID):
        """Get full conversation detail."""
        conversation = await self.repo.get(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise NotFoundError("Conversation", str(conversation_id))
        return conversation

    async def delete_conversation(self, user_id: UUID, conversation_id: UUID) -> None:
        """Delete a conversation."""
        conversation = await self.repo.get(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise NotFoundError("Conversation", str(conversation_id))
        await self.repo.delete(conversation)

    async def _build_context(self, user_id: UUID) -> str:
        """Build rich context from user's profile, recent entries, triggers."""
        context_parts = []

        try:
            from app.repositories.addiction_profile_repository import AddictionProfileRepository
            profile_repo = AddictionProfileRepository(self.db)
            profile = await profile_repo.get_by_user_id(user_id)
            if profile:
                context_parts.append(f"User profile: age={profile.age}, goals={profile.goals}, "
                                     f"bad_habits={profile.bad_habits}, stress={profile.stress_level}/10, "
                                     f"sleep={profile.sleep_hours}h, recovery_style={profile.recovery_style}")
        except Exception:
            pass

        try:
            from app.repositories.journal_repository import JournalRepository
            journal_repo = JournalRepository(self.db)
            recent = await journal_repo.get_recent(user_id, limit=5)
            if recent:
                entry_summaries = []
                for e in recent:
                    entry_summaries.append(
                        f"[{e.created_at.strftime('%m/%d %H:%M')}] {e.entry_type}: "
                        f"emotion={e.emotion}({e.emotion_intensity}/10)"
                        + (f", trigger={e.trigger_app}" if e.trigger_app else "")
                        + (f", notes='{e.notes[:100]}'" if e.notes else "")
                    )
                context_parts.append("Recent journal entries:\n" + "\n".join(entry_summaries))
        except Exception:
            pass

        try:
            from app.repositories.trigger_repository import TriggerRepository
            trigger_repo = TriggerRepository(self.db)
            triggers = await trigger_repo.get_by_user(user_id, limit=3)
            if triggers:
                trigger_summaries = [
                    f"- {t.trigger_type} (frequency: {t.frequency}, confidence: {t.confidence:.0%})"
                    for t in triggers
                ]
                context_parts.append("Known triggers:\n" + "\n".join(trigger_summaries))
        except Exception:
            pass

        return "\n\n".join(context_parts) if context_parts else "No user data available yet."

    async def _get_ai_response(self, messages: list[dict], context: str) -> str:
        """Get AI coach response via LLM."""
        try:
            from app.ai.llm import get_llm_chat_response
            from app.ai.prompts.coach_system import COACH_SYSTEM_PROMPT

            system_prompt = COACH_SYSTEM_PROMPT.format(user_context=context)

            llm_messages = [{"role": "system", "content": system_prompt}]
            # Include last 20 messages for context window
            for msg in messages[-20:]:
                llm_messages.append({"role": msg["role"], "content": msg["content"]})

            return await get_llm_chat_response(llm_messages)

        except Exception as e:
            logger.error("AI coach response failed", error=str(e))
            return self._fallback_response(messages[-1]["content"] if messages else "")

    def _fallback_response(self, user_message: str) -> str:
        """Fallback when LLM is unavailable."""
        msg_lower = user_message.lower()

        if any(w in msg_lower for w in ["craving", "urge", "want to", "tempted"]):
            return ("I hear you — cravings are intense but temporary. They usually peak around 15-20 minutes. "
                    "Can you try a quick change of environment? Even stepping outside for 2 minutes "
                    "can break the pattern. What's one thing you could do right now instead?")
        elif any(w in msg_lower for w in ["relapse", "failed", "messed up", "gave in"]):
            return ("No judgment here. A relapse isn't a reset — it's data. "
                    "What was happening right before? Understanding the 'why' is more valuable "
                    "than beating yourself up. Your streak doesn't define your progress.")
        elif any(w in msg_lower for w in ["bored", "nothing to do", "restless"]):
            return ("Boredom is one of the biggest triggers because your brain craves stimulation. "
                    "Instead of reaching for a quick dopamine hit, try something that builds — "
                    "even 5 minutes of reading, a short walk, or a quick sketch. "
                    "What sounds even slightly interesting right now?")
        elif any(w in msg_lower for w in ["anxious", "stressed", "overwhelmed"]):
            return ("That sounds really tough. When anxiety hits, your brain wants the fastest relief. "
                    "Try this: 4-7-8 breathing — inhale 4 seconds, hold 7, exhale 8. "
                    "Do it 3 times right now. How are you feeling after?")
        else:
            return ("Thanks for reaching out. I'm here to help. "
                    "What's on your mind right now? Are you dealing with a craving, "
                    "want to talk about a trigger, or just need someone to check in with?")
