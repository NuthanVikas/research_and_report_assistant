from utils.llms import LLMModel
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph import Command
from tools.search_tool import search_tool

llm = LLMModel().get_model()

def health_agent(state: AgentState) -> Command[str]:
    """Health research specialist"""
    query = state["messages"][-1].content
    print("\nHealth Agent Active")

    search_results = search_tool.invoke({"query": query})

    prompt = f"""
    You are a medical research specialist. Provide a comprehensive summary of findings
    from the search results for: "{query}"

    Results:
    {search_results}

    Provide detailed medical insights, key findings, and relevant data.
    """

    result = llm.invoke([HumanMessage(content=prompt)])

    return Command(
        goto="research_agent",
        update={
            "messages": [AIMessage(content=f"[HEALTH RESEARCH]\n{result.content}")]
        }
    )
