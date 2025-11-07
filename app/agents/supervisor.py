from langgraph.types import Command
from langgraph.graph import END
from app.core.agent_state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.utils.llms import LLMModel
from app.core.routing_models import SupervisorRouting
from typing import Literal

llm = LLMModel().get_model()

# def supervisor(state: AgentState) -> Command[str]:
#     """Main workflow controller"""
#     print("\nSupervisor Active")

#     research_done = state.get("research_complete", False)
#     report_done = state.get("report_complete", False)

#     if research_done and report_done:
#         print("Both research and report complete! Ending workflow...")
#         final_message = state["messages"][-1].content
#         return Command(
#             goto=END,
#             update={"messages": [AIMessage(content=final_message)]}
#         )

#     if research_done and not report_done:
#         print("Research complete! Routing to report_agent...")
#         return Command(
#             goto="report_agent",
#             update={}
#         )

#     query = state["messages"][-1].content

#     system_prompt = """
# You are the Supervisor Agent of a Research and Report Assistant system.

# Your responsibilities:

# 1. Manage workflow between research_agent and report_agent:
#    - Route tasks to the correct agent based on the user's query.
#    - Track progress of research and report completion.

# 2. Answer general user questions directly:
#    - If the query is a greeting, asking what the system can do, or any non-research/report question, respond directly in plain language.

# Instructions:
# - If the user asks for research or report, route to the appropriate agent.
# - If the user asks a general question, set "next_agent" to "end" and provide a helpful response.
# - Detect if user wants just information or a formal report/PDF
# - Route accordingly through the workflow
# - When the workflow is complete, respond with "end".
# """

#     structured_llm = llm.with_structured_output(SupervisorRouting)
#     decision = structured_llm.invoke([
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=query)
#     ])

#     print(f"Routing to: {decision.next_agent} ({decision.reasoning})")

#     if decision.next_agent == "end":
#         return Command(
#             goto=END,
#             update={"messages": [AIMessage(content=decision.reasoning)]}
#         )
#     else:
#         return Command(
#             goto=decision.next_agent,
#             update={}
#         )



def supervisor(state: AgentState) -> Command[str]:
    """Main workflow controller"""
    print("\nSupervisor Active")

    research_done = state.get("research_complete", False)
    report_done = state.get("report_complete", False)

    # Check if BOTH research and report are complete - END workflow
    if research_done and report_done:
        print("Both research and report complete! Ending workflow...")
        final_message = state["messages"][-1].content
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=final_message)]}
        )

    # If only research is done, check if user wants a report/PDF
    if research_done and not report_done:
        print("Research complete! Checking if user wants a report...")
        
        # Get the original user query (first message)
        original_query = state["messages"][0].content.lower()
        
        # Check if user asked for report/PDF/document
        wants_report = any(keyword in original_query for keyword in [
            'report', 'pdf', 'document', 'doc', 'file', 
            'generate', 'create a report', 'detailed report'
        ])
        
        if wants_report:
            print("User requested report/PDF - routing to report_agent")
            return Command(
                goto="report_agent",
                update={}
            )
        else:
            print("User only wants research - ending workflow")
            final_message = state["messages"][-1].content
            return Command(
                goto=END,
                update={"messages": [AIMessage(content=final_message)]}
            )

    # Initial routing - user's first question
    query = state["messages"][-1].content

    system_prompt = """
You are the Supervisor Agent of a Research and Report Assistant system.

Your responsibilities:

1. Manage workflow between research_agent and report_agent:
   - If user asks for research/information → route to research_agent
   - If user explicitly asks for report/PDF/document → route to research_agent (report will be created after)
   
2. Answer general user questions directly:
   - If the query is a greeting, asking what the system can do, or any non-research/report question, 
     respond directly in plain language and set next_agent to "end".

Instructions:
- For research questions, route to "research_agent"
- For general questions/greetings, set "next_agent" to "end" and provide helpful response
"""

    structured_llm = llm.with_structured_output(SupervisorRouting)
    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    print(f"Routing to: {decision.next_agent} ({decision.reasoning})")

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