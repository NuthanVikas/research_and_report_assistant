from langgraph import Command
from core.agent_state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from utils.llms import LLMModel
from core.routing_models import ReportRouting

llm = LLMModel().get_model()

def report_agent(state: AgentState) -> Command[str]:
    """Coordinates report generation and decides next subagent"""
    print("\nReport Agent Active")

    query = state["messages"][-1].content

    system_prompt = """
    You are the Report Agent Coordinator.

    Your task: analyze the user's query and decide which sub-agent to send it to.

    Available agents:
    - "summary_agent" → if the user asks for a short or concise summary.
    - "document_agent" → if the user requests a detailed or formatted report.
    - "supervisor" → if the input is already a report or not related to report generation.

    Examples:
    - "Summarize WHO heart disease guidelines" → summary_agent
    - "Generate a detailed report on WHO health data" → document_agent
    - "[REPORT] WHO Heart Disease Report" → supervisor (already complete)
    - "What are the next steps?" → supervisor (not a reporting task)

    Return your decision as structured JSON with:
    - next_agent: one of "summary_agent", "document_agent", "supervisor"
    - reasoning: a brief explanation of your choice
    """

    structured_llm = llm.with_structured_output(ReportRouting)

    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    print(f"Routing to: {decision.next_agent}")
    print(f"Reasoning: {decision.reasoning}")

    return Command(
        goto=decision.next_agent,
        update={"messages": [AIMessage(content=f"[ReportAgent] {decision.reasoning}")]}
    )
