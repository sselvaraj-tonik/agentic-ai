from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.core.state import AgentState
from app.modules.supervisor.agent import supervisor_node, route_supervisor
from app.config.settings import settings, PersistenceType

# Import Agent Nodes & Tools
from app.modules.accounts.agent import accounts_agent_node, tools as accounts_tools_list
from app.modules.common.agent import common_agent_node, tools as common_tools_list
from app.modules.loans.agent import loans_agent_node, tools as loans_tools_list

# ==========================================
# AGENT REGISTRY DECLARATION
# ==========================================
# Central array containing your specialized agents. 
# Adding a new domain agent only requires dropping its config here!
AGENT_REGISTRY = [
    {"name": "accounts", "node": accounts_agent_node, "tools": accounts_tools_list},
    {"name": "common", "node": common_agent_node, "tools": common_tools_list},
    # {"name": "loans", "node": loans_agent_node, "tools": loans_tools_list},
]

# ==========================================
# DYNAMIC ROUTING LOGIC FACTORY
# ==========================================
def create_tools_condition(tool_node_name: str):
    """Dynamically generates a unique tool routing closure for an agent."""
    return lambda state: tool_node_name if state["messages"][-1].tool_calls else END


# ==========================================
# GRAPH CONSTRUCTION
# ==========================================
def build_graph():
    builder = StateGraph(AgentState)

    # 1. Add Core Orchestrator (Supervisor)
    builder.add_node("supervisor", supervisor_node)
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_supervisor)

    # 2. Dynamically Loop, Register, and Wire All Specialized Agents
    for agent_config in AGENT_REGISTRY:
        agent_name = f"{agent_config['name']}_agent"
        tool_name = f"{agent_config['name']}_tools"

        # Add Core Logic and Tool Nodes
        builder.add_node(agent_name, agent_config["node"])
        builder.add_node(tool_name, ToolNode(agent_config["tools"]))

        # Agent -> Tool Routing Edge
        tools_condition = create_tools_condition(tool_name)
        builder.add_conditional_edges(agent_name, tools_condition)

        # Tool -> Agent Loopback Edge
        builder.add_edge(tool_name, agent_name)

    # 3. Initialize Checkpointer Based on Configuration
    if settings.PERSISTENCE_TYPE == PersistenceType.POSTGRES:
        # CRITICAL FIX: Explicitly add autocommit=True and row_factory=dict_row
        # to prevent Postgres ActiveSqlTransaction errors during migrations.
        pool = ConnectionPool(
            conninfo=settings.DATABASE_URL, 
            max_size=10,
            kwargs={"autocommit": True, "row_factory": dict_row}
        )
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()  # This now executes successfully outside transaction blocks
    else:
        checkpointer = MemorySaver()

    # Compile the final agent executor
    return builder.compile(checkpointer=checkpointer)

# Singleton instance
graph_executor = build_graph()