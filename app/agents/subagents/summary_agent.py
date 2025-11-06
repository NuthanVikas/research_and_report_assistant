from app.utils.llms import LLMModel
from app.core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

llm = LLMModel().get_model()

def summary_agent(state: AgentState) -> Command[str]:
    """Creates concise summaries"""
    content = state["messages"][-1].content
    print("\nSummary Agent Active")

    prompt = f"""
    Create a concise executive summary of the following research content.
    Focus on key insights, main findings, and actionable takeaways.

    Content:
    {content}
    """
    
    result = llm.invoke([HumanMessage(content=prompt)])
    
    return Command(
        goto="report_agent",
        update={"messages": [AIMessage(content=f"[SUMMARY]\n{result.content}")]}
    )
