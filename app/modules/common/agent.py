from langchain_core.messages import SystemMessage
from app.core.state import AgentState
from app.core.llm import get_llm
from app.modules.common.tools import search_company_knowledge

llm = get_llm()
# Add the tools for the common agent
tools = [search_company_knowledge]
common_llm = llm.bind_tools(tools)

def common_agent_node(state: AgentState):
    prompt = SystemMessage(content="""You are the Common Agent.
    You handle general banking questions and FAQs.

    FAQ & COMPANY INFO: If the user asks general questions about the company, policies, or FAQs, ALWAYS call the 'search_company_knowledge' tool.""")
    response = common_llm.invoke([prompt] + state["messages"])
    return {"messages": [response]}
