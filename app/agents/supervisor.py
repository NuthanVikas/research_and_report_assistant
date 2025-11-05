from langgraph import Command, END
from core.agent_state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from utils.llms import LLMModel
from core.routing_models import SupervisorRouting

llm = LLMModel().get_model()

def supervisor(state: AgentState) -> Command[str]:
    """Main workflow controller"""
    print("\nSupervisor Active")

    research_done = state.get("research_complete", False)
    report_done = state.get("report_complete", False)

    if research_done and report_done:
        print("Workflow complete!")
        final_message = state.get("final_output", state["messages"][-1].content)
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=final_message)]}
        )

    query = state["messages"][-1].content

    system_prompt = """
    You are a supervisor tasked with managing a conversation between research_agent and report_agent.
    Given the following user request, respond with which worker should act next.
    Each worker will perform a task and respond with their results and status.
    When finished, respond with "end".
    """

    structured_llm = llm.with_structured_output(SupervisorRouting)
    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    print(f"Routing to: {decision.next_agent} ({decision.reasoning})")

    if decision.next_agent == "end":
        return Command(goto=END, update={})

    return Command(goto=decision.next_agent, update={})
