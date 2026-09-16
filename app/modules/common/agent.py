from langchain_core.messages import HumanMessage, AIMessage

from app.core.state import AgentState
from app.core.decorators import log_execution_time
from app.modules.knowledge import answer_query
from app.modules.knowledge.render import to_text

# The common agent has no LLM tools: it runs the deterministic knowledge funnel
# (spell -> small talk -> ontology -> FAQ -> open-text RAG -> fallback). The
# graph builder skips wiring a tool node when this list is empty.
tools = []


def _latest_user_text(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage) and isinstance(msg.content, str):
            return msg.content
    last = state["messages"][-1]
    return last.content if isinstance(last.content, str) else str(last.content)


@log_execution_time
def common_agent_node(state: AgentState):
    """
    Resolve the user's message through the knowledge inference pipeline and
    return its answer directly. Verbatim tiers (small talk, FAQ, ontology) and
    the fallback answer without any LLM; only the open-text RAG tier generates.
    """
    query = _latest_user_text(state)
    result = answer_query(query)
    return {"messages": [AIMessage(content=to_text(result))]}
