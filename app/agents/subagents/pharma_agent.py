from app.utils.llms import LLMModel
from app.core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from app.tools.search_tool import search_tool
from typing import Literal

llm = LLMModel().get_model()

def pharma_agent(state: AgentState) -> Command[str]:
    """Pharmaceutical research specialist"""
    query = state["messages"][-1].content
    print("\nPharma Agent Active")

    search_results = search_tool.invoke({"query": query})

    prompt = f"""
    You are a pharmaceutical research assistant. Provide structured insights for: "{query}"

    Results:
    {search_results}

    Focus on drug information, pharmaceutical trends, and market analysis.
    """

    result = llm.invoke([HumanMessage(content=prompt)])

    return Command(
        goto="research_agent",
        update={
            "messages": [AIMessage(content=f"[PHARMA RESEARCH]\n{result.content}")]
        }
    )
