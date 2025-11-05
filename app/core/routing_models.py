from pydantic import BaseModel
from typing import Literal

class ResearchRouting(BaseModel):
    """Decision model for research agent routing"""
    next_agent: Literal["health_agent", "pharma_agent", "supervisor"]
    reasoning: str

class ReportRouting(BaseModel):
    """Decision model for report agent routing"""
    next_agent: Literal["summary_agent", "document_agent", "supervisor"]
    reasoning: str

class SupervisorRouting(BaseModel):
    """Decision model for supervisor routing"""
    next_agent: Literal["research_agent", "report_agent", "end"]
    reasoning: str
