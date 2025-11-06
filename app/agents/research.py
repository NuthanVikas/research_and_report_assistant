from langgraph.types import Command
from app.core.agent_state import AgentState
from app.utils.llms import LLMModel
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.routing_models import ResearchRouting
from app.agents.subagents.health_agent import health_agent
from app.agents.subagents.pharma_agent import pharma_agent
from typing import Literal

llm = LLMModel().get_model()

def research_agent(state: AgentState) -> Command[str]:
    """Research Agent Coordinator"""
    print("\nResearch Agent Active")

    query = state["messages"][-1].content

    system_prompt = """
    You are the Research Agent Coordinator.

    Your task is to decide where to send the query next.
    Choose from these:
    - "health_agent" → for medical, clinical, or public health research
    - "pharma_agent" → for drugs, pharmaceuticals, biotech, or market research
    - "supervisor" → for non-research queries or when research is complete

    Rules:
    1. If the query already contains research results (e.g. starts with [HEALTH RESEARCH] or [PHARMA RESEARCH]),
       route it to the "supervisor".
    2. If the user is asking for medical or lifestyle information, choose "health_agent".
    3. If the user is asking about drugs, trials, or pharma-related topics, choose "pharma_agent".
    4. Otherwise, choose "supervisor".

    Return your answer in structured format:
    {
      "next_agent": "<agent_name>",
      "reasoning": "<why you chose this>"
    }
    """

    # Use structured output with Pydantic model
    structured_llm = llm.with_structured_output(ResearchRouting)

    decision = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    print(f"Routing Decision → {decision.next_agent}")
    print(f"Reasoning: {decision.reasoning}")

    # return Command(goto=decision.next_agent, update={"research_complete": True})
    
    if decision.next_agent == "supervisor":
      return Command(goto=decision.next_agent, update={"research_complete": True})
    else:
      return Command(goto=decision.next_agent, update={})

