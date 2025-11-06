from langgraph.graph import StateGraph, START, END
from app.core.agent_state import AgentState
from app.agents.supervisor import supervisor
from app.agents.research import research_agent
from app.agents.report import report_agent
from app.agents.subagents.health_agent import health_agent
from app.agents.subagents.pharma_agent import pharma_agent
from app.agents.subagents.summary_agent import summary_agent
from app.agents.subagents.document_agent import document_agent

def create_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("research_agent", research_agent)
    graph.add_node("report_agent", report_agent)
    graph.add_node("health_agent", health_agent)
    graph.add_node("pharma_agent", pharma_agent)
    graph.add_node("summary_agent", summary_agent)
    graph.add_node("document_agent", document_agent)

    graph.add_edge(START, "supervisor")
    graph.add_edge("health_agent", "research_agent")
    graph.add_edge("pharma_agent", "research_agent")
    graph.add_edge("summary_agent", "report_agent")
    graph.add_edge("document_agent", "report_agent")

    graph_app = graph.compile()
    return graph_app