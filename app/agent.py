import os
import httpx
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.tools import get_customer_profile

load_dotenv()

# Define the tools list
tools = [get_customer_profile]

# Initialize the LLM
model_name = os.getenv("OLLAMA_MODEL", "llama3")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Initialize ChatOllama
# We don't try/except here because ChatOllama initialization is lazy.
# The error usually happens at invocation time.
llm = ChatOllama(
    model=model_name,
    base_url=base_url,
    temperature=0
)

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)

def reasoner_node(state: MessagesState):
    """
    The main reasoning node that calls the LLM.
    Wraps the LLM call in a try/except to catch connection errors.
    """
    try:
        # Invoke the LLM with the current conversation history
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    except (httpx.ConnectError, httpx.RequestError) as e:
        # Return a system message indicating the connection failure
        # This prevents the app from crashing and gives the user feedback
        error_msg = (
            f"**Error**: Could not connect to the AI model provider (Ollama) at `{base_url}`.\n"
            f"Please ensure that Ollama is running and accessible.\n"
            f"Technical details: {str(e)}"
        )
        # We return a simple text response masking as an AI message for simplicity in the UI
        # In a more complex app, you might want a special Error Node.
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content=error_msg)]}

# Create the graph builder
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("reasoner", reasoner_node)
builder.add_node("tools", ToolNode(tools))

# Define edges
builder.add_edge(START, "reasoner")

# Conditional edge: checks if the LLM requested a tool call
builder.add_conditional_edges(
    "reasoner",
    tools_condition,
)

# After tool execution, loop back to reasoner to interpret results
builder.add_edge("tools", "reasoner")

# Compile the graph
agent_executor = builder.compile()
