from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.core.state import AgentState
from app.modules.supervisor.agent import supervisor_node, route_supervisor

# Import Agent Nodes
from app.modules.accounts.agent import accounts_agent_node, tools as accounts_tools_list
from app.modules.transfers.agent import transfers_agent_node, tools as transfers_tools_list
from app.modules.loans.agent import loans_agent_node, tools as loans_tools_list

# ==========================================
# CONDITIONAL ROUTING LOGIC
# ==========================================

# Custom tool routing conditions for each specialized agent
def accounts_tools_condition(state: AgentState):
    if state["messages"][-1].tool_calls: return "accounts_tools"
    return END

def transfers_tools_condition(state: AgentState):
    if state["messages"][-1].tool_calls: return "transfers_tools"
    return END

def loans_tools_condition(state: AgentState):
    if state["messages"][-1].tool_calls: return "loans_tools"
    return END


# ==========================================
# GRAPH CONSTRUCTION
# ==========================================

def build_graph():
    builder = StateGraph(AgentState)

    # Add standard nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("accounts_agent", accounts_agent_node)
    builder.add_node("transfers_agent", transfers_agent_node)
    builder.add_node("loans_agent", loans_agent_node)

    # Add isolated tool nodes
    builder.add_node("accounts_tools", ToolNode(accounts_tools_list))
    builder.add_node("transfers_tools", ToolNode(transfers_tools_list))
    builder.add_node("loans_tools", ToolNode(loans_tools_list))

    # Entry point -> Always start at the Supervisor
    builder.add_edge(START, "supervisor")

    # Supervisor -> Agent Routing
    builder.add_conditional_edges("supervisor", route_supervisor)

    # Agent -> Tool Routing (or END if they just replied to the user)
    builder.add_conditional_edges("accounts_agent", accounts_tools_condition)
    builder.add_conditional_edges("transfers_agent", transfers_tools_condition)
    builder.add_conditional_edges("loans_agent", loans_tools_condition)

    # Tool -> Agent looping (tools send data back to their specific agent)
    builder.add_edge("accounts_tools", "accounts_agent")
    builder.add_edge("transfers_tools", "transfers_agent")
    builder.add_edge("loans_tools", "loans_agent")

    # Initialize memory checkpointer for stateful conversations
    memory = MemorySaver()

    # Compile the final agent executor
    agent_executor = builder.compile(checkpointer=memory)

    return agent_executor

# Singleton instance
graph_executor = build_graph()
