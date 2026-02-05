import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END

load_dotenv()
from langgraph.prebuilt import ToolNode, tools_condition
from app.tools import get_customer_profile

# Define the tools list
tools = [get_customer_profile]

# Initialize the LLM
# Using environment variables for configuration allows flexibility in production
# Default to 'llama3' which is a strong open source model
model_name = os.getenv("OLLAMA_MODEL", "llama3")
# Default Ollama port
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = ChatOllama(
    model=model_name,
    base_url=base_url,
    temperature=0  # Low temperature for more deterministic actions
)

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)

def reasoner_node(state: MessagesState):
    """
    The main reasoning node that calls the LLM.
    """
    # Invoke the LLM with the current conversation history
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Create the graph builder
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("reasoner", reasoner_node)
builder.add_node("tools", ToolNode(tools))

# Define edges
builder.add_edge(START, "reasoner")

# Conditional edge: checks if the LLM requested a tool call
# If yes -> goes to "tools", If no -> goes to END
builder.add_conditional_edges(
    "reasoner",
    tools_condition,
)

# After tool execution, loop back to reasoner to interpret results
builder.add_edge("tools", "reasoner")

# Compile the graph
agent_executor = builder.compile()
