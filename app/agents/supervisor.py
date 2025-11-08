from __future__ import annotations

from typing import Sequence

from langgraph.graph import END
from langgraph.types import Command

from app.core.agent_state import AgentState
from app.core.routing_models import SupervisorRouting
from app.utils.llms import LLMModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

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


def supervisor(state: AgentState) -> Command[str]:
    """Main workflow controller"""
    print("\nSupervisor Active")

    messages: Sequence[BaseMessage] = state.get("messages", [])
    latest_message = messages[-1] if messages else None
    latest_text = _stringify(latest_message)
    first_request = _stringify(next((msg for msg in messages if isinstance(msg, HumanMessage)), None))

    research_done = state.get("research_complete", False)
    report_done = state.get("report_complete", False)

    if research_done and report_done:
        print("Both research and report complete! Ending workflow...")
        final_message = latest_text or "Workflow completed."
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=final_message)]},
        )

    system_prompt = """
You are the Supervisor Agent of a Research and Report Assistant system focused on health and pharma research.

Responsibilities:
1. Determine which specialist should act next.
2. Only answer directly when the user is making small talk (greetings, asking about capabilities, etc.).

Routing guidance:
- If the user asks for information, research, or insights about a health/pharma topic, ALWAYS route to "research_agent" first.
- After research completes, decide whether a follow-up summary/document is needed based on the user's original request.
- Route to "report_agent" only when the user explicitly wants a summary, formal report, PDF, or similar deliverable.
- Use "end" strictly for greetings, non-domain chit-chat, or when the workflow is finished.
- Include clear reasoning for every choice.
"""

    structured_llm = llm.with_structured_output(SupervisorRouting)
    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Original user request:\n{first_request or 'N/A'}\n\n"
                f"Most recent message:\n{latest_text}\n\n"
                f"Research complete: {research_done}\n"
                f"Report complete: {report_done}\n"
                "Decide the next step."
            )
        )
    ])

    print(f"Routing to: {decision.next_agent} ({decision.reasoning})")

    if decision.next_agent == "end":
        if research_done and not report_done:
            final_content = latest_text or "Research completed."
        else:
            response_text = decision.response.strip()
            final_content = response_text or decision.reasoning

        return Command(
            goto=END,
            update={"messages": [AIMessage(content=final_content)]}
        )
    else:
        return Command(
            goto=decision.next_agent,
            update={}
        )
