"""
Model registry — imports all models so Alembic and relationships work correctly.
"""

from app.models.addiction_profile import AddictionProfile
from app.models.assessment import Assessment
from app.models.conversation import Conversation
from app.models.gamification import Gamification
from app.models.journal_entry import JournalEntry
from app.models.recovery_score import RecoveryScore
from app.models.refresh_token import RefreshToken
from app.models.trigger import Trigger
from app.models.user import User

__all__ = [
    "User",
    "RefreshToken",
    "AddictionProfile",
    "Assessment",
    "JournalEntry",
    "Trigger",
    "Conversation",
    "RecoveryScore",
    "Gamification",
]
