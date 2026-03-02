from langchain_core.messages import SystemMessage
from app.core.state import AgentState
from app.core.llm import get_llm

llm = get_llm()
# Currently an empty structure as requested. Tools will be added later.
tools = []
common_llm = llm

def common_agent_node(state: AgentState):
    prompt = SystemMessage(content="""You are the Common Agent.
    You handle general banking questions and FAQs.
    (This is currently a placeholder until specific requirements are provided).""")
    response = common_llm.invoke([prompt] + state["messages"])
    return {"messages": [response]}
