"""
Assessment schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssessmentStartRequest(BaseModel):
    addiction_type: str = Field(..., max_length=50)


class AssessmentStartResponse(BaseModel):
    assessment_id: UUID
    addiction_type: str
    questions: list[dict]  # [{"id": "q1", "text": "...", "type": "scale|choice|text", "options": [...]}]


class AssessmentSubmitRequest(BaseModel):
    assessment_id: UUID
    responses: dict  # {"q1": 8, "q2": "daily", "q3": "When I'm bored"}


class AssessmentResultResponse(BaseModel):
    id: UUID
    addiction_type: str
    addiction_score: int
    risk_score: int
    recovery_difficulty: str
    ai_analysis: str | None
    assessed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentHistoryResponse(BaseModel):
    assessments: list[AssessmentResultResponse]
    total: int
