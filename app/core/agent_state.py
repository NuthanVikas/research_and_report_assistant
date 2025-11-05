from typing import Sequence, TypedDict
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    research_complete: bool
    report_complete: bool
    final_output: str
