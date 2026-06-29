"""
AI Coach Agent using LangGraph.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.ai.agents.state import CoachState
from app.ai.prompts.coach_system import COACH_SYSTEM_PROMPT
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_coach_graph():
    """Build the LangGraph for the AI Coach."""
    from langchain_openai import ChatOpenAI

    # We use ChatOpenAI connected to OpenRouter for Litellm-compatible routing
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=settings.llm_temperature,
    )

    # Define tools if we want the agent to call functions (e.g., log a journal entry for them)
    # tools = [log_craving, get_breathing_exercise]
    # tool_node = ToolNode(tools)
    # llm_with_tools = llm.bind_tools(tools)
    llm_with_tools = llm  # Future Phase: Bind tools to let agent take actions

    def analyze_context(state: CoachState):
        """Analyze the context to determine risk level before generating response."""
        messages = state["messages"]
        last_message = messages[-1].content.lower()

        risk_level = "low"
        if any(w in last_message for w in ["relapse", "gave in", "messed up", "failed"]):
            risk_level = "high"
        elif any(w in last_message for w in ["craving", "urge", "want", "tempted", "need"]):
            risk_level = "moderate"

        return {"risk_level": risk_level}

    def generate_response(state: CoachState):
        """Generate the coach's response."""
        messages = state["messages"]
        context = state.get("user_context", "No context provided.")
        risk_level = state.get("risk_level", "low")

        system_prompt = COACH_SYSTEM_PROMPT.format(user_context=context)

        # Add instructions based on risk
        if risk_level == "high":
            system_prompt += "\n\nCRITICAL: The user has likely relapsed or is in high distress. Prioritize immediate compassion, de-escalation, and identifying the trigger. Do not talk about streaks."
        elif risk_level == "moderate":
            system_prompt += "\n\nCRITICAL: The user is experiencing a craving. Prioritize environmental change, distraction, or grounding exercises."

        # Prepend system message
        messages_to_send = [SystemMessage(content=system_prompt)] + list(messages)

        response = llm_with_tools.invoke(messages_to_send)
        return {"messages": [response]}

    # Build graph
    workflow = StateGraph(CoachState)

    workflow.add_node("analyze", analyze_context)
    workflow.add_node("respond", generate_response)

    # Set entry point
    workflow.set_entry_point("analyze")

    # Define edges
    workflow.add_edge("analyze", "respond")
    workflow.add_edge("respond", END)

    # Compile
    return workflow.compile()


# Global instance
coach_agent = None


def get_coach_agent():
    """Get or create the compiled LangGraph agent."""
    global coach_agent
    if not coach_agent:
        coach_agent = create_coach_graph()
    return coach_agent


async def chat_with_langgraph_coach(user_message: str, context: str, history: list = None) -> str:
    """Wrapper function to invoke the LangGraph agent."""
    agent = get_coach_agent()

    messages = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                from langchain_core.messages import HumanMessage
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    result = await agent.ainvoke({
        "messages": messages,
        "user_context": context
    })

    return result["messages"][-1].content
