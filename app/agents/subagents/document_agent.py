from utils import LLMModel
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from langgraph import Command

llm = LLMModel().get_model()

def document_agent(state: AgentState) -> Command[str]:
    """Formats professional reports"""
    content = state["messages"][-1].content
    print("\nDocument Agent Active")

    prompt = f"""
    Format the following content into a professional report with these sections:
    
    # Title
    ## Abstract
    ## Key Findings
    ## Recommendations
    ## Conclusion

    Content:
    {content}

    Your task is to convert the summarized information to PDF or doc format.
    """
    
    result = llm.invoke([HumanMessage(content=prompt)])
    
    return Command(
        goto="report_agent",
        update={"messages": [AIMessage(content=f"[REPORT]\n{result.content}")] }
    )
