from __future__ import annotations

from langgraph.types import Command

from app.core.agent_state import AgentState
from app.core.routing_models import ReportRouting
from app.utils.llms import LLMModel
from langchain_core.messages import HumanMessage, SystemMessage

llm = LLMModel().get_model()


def _prefixed_route(message: str) -> str | None:
    first_line = message.strip().split("\n", 1)[0].strip()
    if first_line.startswith("[HEALTH RESEARCH]") or first_line.startswith("[PHARMA RESEARCH]"):
        return "summary_agent"
    if first_line.startswith("[SUMMARY]"):
        return "document_agent"
    if first_line.startswith("[REPORT]"):
        return "complete"
    return None


def report_agent(state: AgentState) -> Command[str]:
    """Coordinates report generation and determines follow-up steps."""
    print("\nReport Agent Active")

    latest_message = state["messages"][-1].content
    routed = _prefixed_route(latest_message)

    if routed == "summary_agent":
        return Command(goto="summary_agent", update={})

    if routed == "document_agent":
        return Command(goto="document_agent", update={})

    if routed == "complete":
        return Command(
            goto="supervisor",
            update={
                "report_complete": True,
                "final_output": latest_message,
            },
        )

    system_prompt = """
    You are the Report Agent Coordinator.

    Your task: analyze the user's query and decide which sub-agent should act next.

    Available agents:
    - "summary_agent" → when a concise executive summary is needed.
    - "document_agent" → when a detailed, polished report is required.
    - "supervisor" → when the request is already complete or unrelated to reporting.

    Return a JSON object with:
      - next_agent: one of "summary_agent", "document_agent", "supervisor"
      - reasoning: explanation of the choice
    """

    decision = llm.with_structured_output(ReportRouting).invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=latest_message),
        ]
    )

    print(f"Routing to: {decision.next_agent}")
    print(f"Reasoning: {decision.reasoning}")

    if decision.next_agent == "supervisor":
        return Command(
            goto="supervisor",
            update={
                "report_complete": True,
                "final_output": latest_message,
            },
        )

    return Command(goto=decision.next_agent, update={})
