"""
Agent state definitions for LangGraph.
"""

from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CoachState(TypedDict):
    """
    State for the AI Recovery Coach.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_context: str
    risk_level: str
    suggested_action: str | None
    next_step: str
