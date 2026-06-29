"""
Trigger service — analyzes journal entries to discover relapse patterns.
"""

from collections import Counter
from datetime import UTC, datetime
from itertools import combinations
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.journal_repository import JournalRepository
from app.repositories.trigger_repository import TriggerRepository

logger = get_logger(__name__)


class TriggerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.journal_repo = JournalRepository(db)
        self.trigger_repo = TriggerRepository(db)

    async def analyze_triggers(self, user_id: UUID) -> list:
        """Analyze recent journal entries to find trigger patterns."""
        # Get recent entries focused on cravings and relapses
        entries = await self.journal_repo.get_recent(user_id, limit=50)
        risk_entries = [
            e for e in entries
            if e.entry_type in ("craving", "relapse")
        ]

        if len(risk_entries) < 3:
            return []  # Not enough data

        # Extract context dimensions from each entry
        entry_contexts = []
        for entry in risk_entries:
            context = {}
            if entry.emotion:
                context["emotion"] = entry.emotion
            if entry.time_of_day:
                context["time_of_day"] = entry.time_of_day
            if entry.location:
                context["location"] = entry.location
            if entry.device:
                context["device"] = entry.device
            if entry.trigger_app:
                context["app"] = entry.trigger_app
            if entry.people_context:
                context["social"] = entry.people_context
            if entry.stress_level and entry.stress_level >= 7:
                context["high_stress"] = True
            if entry.sleep_hours_last_night and entry.sleep_hours_last_night < 6:
                context["poor_sleep"] = True
            if entry.energy_level and entry.energy_level <= 3:
                context["low_energy"] = True

            # Day of week from timestamp
            if entry.created_at:
                context["day_of_week"] = entry.created_at.strftime("%A").lower()

            entry_contexts.append(context)

        # Find frequent patterns (co-occurring features)
        discovered_patterns = self._find_patterns(entry_contexts, min_frequency=2)

        # Upsert trigger records
        results = []
        for pattern, frequency in discovered_patterns:
            trigger_type = " + ".join(f"{k}={v}" for k, v in sorted(pattern.items()))
            confidence = min(1.0, frequency / len(risk_entries))

            # Check if pattern already exists
            existing = await self.trigger_repo.find_matching_pattern(user_id, pattern)
            if existing:
                trigger = await self.trigger_repo.update(
                    existing,
                    frequency=frequency,
                    confidence=confidence,
                    last_triggered_at=datetime.now(UTC),
                )
            else:
                # Generate insight
                insight = self._generate_insight(pattern, frequency, len(risk_entries))

                trigger = await self.trigger_repo.create(
                    user_id=user_id,
                    trigger_type=trigger_type,
                    pattern=pattern,
                    frequency=frequency,
                    confidence=confidence,
                    insight=insight,
                    discovered_at=datetime.now(UTC),
                )

            results.append(trigger)

        logger.info(
            "Trigger analysis complete",
            user_id=str(user_id),
            patterns_found=len(results),
        )
        return results

    def _find_patterns(
        self, contexts: list[dict], min_frequency: int = 2
    ) -> list[tuple[dict, int]]:
        """Find frequently co-occurring context features."""
        patterns = []

        # Check pairs and triples of features
        for size in (2, 3):
            pair_counter: Counter = Counter()

            for ctx in contexts:
                items = [(k, v) for k, v in ctx.items() if v is not True]
                bool_items = [(k, "true") for k, v in ctx.items() if v is True]
                all_items = items + bool_items

                for combo in combinations(all_items, min(size, len(all_items))):
                    pair_counter[combo] += 1

            for combo, freq in pair_counter.most_common(10):
                if freq >= min_frequency:
                    pattern = dict(combo)
                    patterns.append((pattern, freq))

        # Deduplicate — keep higher-order patterns that subsume lower-order ones
        patterns.sort(key=lambda x: (-len(x[0]), -x[1]))
        seen_keys = set()
        unique_patterns = []
        for pattern, freq in patterns:
            key = frozenset(pattern.items())
            # Check if this is a subset of an already-seen pattern
            is_subset = any(key < seen for seen in seen_keys)
            if not is_subset:
                unique_patterns.append((pattern, freq))
                seen_keys.add(key)

        return unique_patterns[:10]  # Top 10 patterns

    def _generate_insight(self, pattern: dict, frequency: int, total_entries: int) -> str:
        """Generate a human-readable insight from a pattern."""
        parts = []
        for key, value in pattern.items():
            if key == "emotion":
                parts.append(f"feeling {value}")
            elif key == "time_of_day":
                parts.append(f"during the {value}")
            elif key == "location":
                parts.append(f"at {value}")
            elif key == "device":
                parts.append(f"on your {value}")
            elif key == "app":
                parts.append(f"after using {value}")
            elif key == "social":
                parts.append(f"when {value}")
            elif key == "day_of_week":
                parts.append(f"on {value.capitalize()}s")
            elif key == "high_stress":
                parts.append("under high stress")
            elif key == "poor_sleep":
                parts.append("after poor sleep")
            elif key == "low_energy":
                parts.append("with low energy")

        percentage = int((frequency / total_entries) * 100)
        description = ", ".join(parts)

        return (
            f"In {percentage}% of your cravings/relapses, you were {description}. "
            f"This pattern appeared {frequency} times."
        )

    async def get_user_triggers(self, user_id: UUID, limit: int = 10) -> list:
        """Get top triggers for a user."""
        return await self.trigger_repo.get_by_user(user_id, limit)
