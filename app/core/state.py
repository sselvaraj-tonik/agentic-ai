from typing import Literal, TypedDict, List
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    State for the banking agent.
    Inherits from MessagesState to store chat history.
    """
    next_node: str

class RouteResponse(BaseModel):
    """
    Structured response from the supervisor LLM.
    """
    next_node: Literal["accounts_agent", "common_agent", "loans_agent", "FINISH"] = Field(
        description="The exact agent to route the user to based on their request. Use FINISH if the user's task is done."
    )
