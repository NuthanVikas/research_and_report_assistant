from langgraph.types import Command
from langgraph.graph import END
from app.core.agent_state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.utils.llms import LLMModel
from app.core.routing_models import SupervisorRouting
from typing import Literal

llm = LLMModel().get_model()

def supervisor(state: AgentState) -> Command[str]:
    """Main workflow controller"""
    print("\nSupervisor Active")

    research_done = state.get("research_complete", False)
    report_done = state.get("report_complete", False)

    # if research_done and report_done:
    #     print("Workflow complete!")
    #     final_message = state.get("final_output", state["messages"][-1].content)
    #     return Command(
    #         goto=END,
    #         update={"messages": [AIMessage(content=final_message)]}
    #     )

    if research_done:
        print("Research complete! Checking messages...")
    
        # Get the last message content (should be the health agent's research)
        final_message = state["messages"][-1].content
    
        #If it contains research results, we're done
        if "[HEALTH RESEARCH]" in final_message or "[PHARMA RESEARCH]" in final_message:
            return Command(
                goto=END,
                update={"messages": [AIMessage(content=final_message)]}
            )

    if research_done and report_done:
        print("Both research and report complete! Ending workflow...")
        final_message = state["messages"][-1].content
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=final_message)]}
        )

    # # If only research is done, route to report_agent for summary
    # if research_done and not report_done:
    #     print("Research complete! Routing to report_agent for summary...")
    #     final_message = state["messages"][-1].content
    
    #     # Check if this is research results that need to be summarized
    #     if "[HEALTH RESEARCH]" in final_message or "[PHARMA RESEARCH]" in final_message:
    #         return Command(
    #             goto="report_agent",
    #             update={}
    #         )

    query = state["messages"][-1].content

    system_prompt = """
You are the Supervisor Agent of a Research and Report Assistant system.

Your responsibilities:

1. Manage workflow between research_agent and report_agent:
   - Route tasks to the correct agent based on the user's query.
   - Track progress of research and report completion.

2. Answer general user questions directly:
   - If the query is a greeting, asking what the system can do, or any non-research/report question, respond directly in plain language.

Instructions:
- If routing to an agent, return structured JSON with "next_agent" and "reasoning".
- If answering directly, set "next_agent" to "end" and provide a helpful response in "reasoning".
- When the workflow is complete, respond with "end".
"""

    structured_llm = llm.with_structured_output(SupervisorRouting)
    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    print(f"Routing to: {decision.next_agent} ({decision.reasoning})")

    # return Command(
    #     goto=END,
    #     update={"messages": [AIMessage(content=decision.reasoning)]}
    # )
   

    if decision.next_agent == "end":
        return Command(
        goto=END,
        update={"messages": [AIMessage(content=decision.reasoning)]}
    )
    else:
        return Command(
            goto=decision.next_agent,
            update={}
    )
 