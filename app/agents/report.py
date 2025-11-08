from __future__ import annotations

from typing import Any, Sequence

from langgraph.types import Command
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.core.agent_state import AgentState
from app.core.routing_models import ReportRouting
from app.utils.llms import LLMModel

llm = LLMModel().get_model()


def _stringify(message: BaseMessage | None) -> str:
    if message is None:
        return ""
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            (
                fragment.get("text", "")
                if isinstance(fragment, dict)
                else str(fragment)
            ).strip()
            for fragment in content
        )
    return str(content)


def _latest_user_request(messages: Sequence[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return _stringify(message).strip()
    return "No explicit user request found."


def _finalize(latest_text: str) -> Command[str]:
    final_text = latest_text.strip() or "Report agent did not receive content to finalize."
    return Command(
        goto="supervisor",
        update={
            "report_complete": True,
            "final_output": final_text,
        },
    )


def report_agent(state: AgentState) -> Command[str]:
    """Decide next reporting step using the LLM (summary, document, or finalize)."""
    print("\nReport Agent Active")

    messages: Sequence[BaseMessage] = state.get("messages", [])
    latest_text = _stringify(messages[-1] if messages else None)
    user_request = _latest_user_request(messages)

    routing_prompt = """
You are the report coordinator in a multi-agent workflow.
Given the user's latest request and the current content, decide what should happen next:

- Choose "summary_agent" when the user needs a concise executive summary.
- Choose "document_agent" when the user needs a detailed report, formatted document, or PDF.
- Choose "supervisor" when the content is already final or no further reporting work is required.

Return a JSON object with:
  - next_agent: "summary_agent", "document_agent", or "supervisor"
  - reasoning: brief explanation grounded in the user request and content
"""

    decision = llm.with_structured_output(ReportRouting).invoke(
        [
            SystemMessage(content=routing_prompt.strip()),
            HumanMessage(
                content=(
                    f"User request:\n{user_request}\n\n"
                    f"Current content to evaluate:\n{latest_text}\n"
                )
            ),
        ]
    )

    print(f"Report routing → {decision.next_agent} ({decision.reasoning})")

    if decision.next_agent == "supervisor":
        return _finalize(latest_text)

    return Command(goto=decision.next_agent, update={})
