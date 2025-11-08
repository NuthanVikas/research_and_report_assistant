from app.utils.llms import LLMModel
from app.core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from app.tools.search_tool import search_tool
from typing import Literal

llm = LLMModel().get_model()

def health_agent(state: AgentState) -> Command[str]:
    """Health research specialist"""
    
    print("\nHealth Agent Active")
    query = state["messages"][-1].content

    search_results = search_tool.invoke({"query": query})

    prompt = f"""
    Your task is to conduct in-depth research and gather accurate, evidence-based information on topics related to health, medicine, or clinical research for: "{query}"

    Results:
    {search_results}

    Provide detailed medical insights, key findings, and relevant data.
    """

    result = llm.invoke([HumanMessage(content=prompt)])
    formatted_content = result.content.strip()

    return Command(
        goto="research_agent",
        update={
            "messages": [AIMessage(content=f"HEALTH RESEARCH:\n{formatted_content}")]
        }
    )
