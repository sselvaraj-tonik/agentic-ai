from langchain_core.messages import SystemMessage
from app.core.state import AgentState
from app.core.llm import get_llm
from app.modules.common.tools import search_company_knowledge
from app.core.decorators import log_execution_time

llm = get_llm()
# Add the tools for the common agent
tools = [search_company_knowledge]
common_llm = llm.bind_tools(tools)

@log_execution_time
def common_agent_node(state: AgentState):
    prompt = SystemMessage(content="""You are the Common Agent for Tonik Bank. 
    Your primary job is to answer general banking questions, "how-to" inquiries, and FAQs.

    STRICT RULES:
    1. MANDATORY TOOL USE: For ANY question about the bank, its features, or FAQs, you MUST call the 'search_company_knowledge' tool.
    2. NO HALLUCINATION: You must base your answer EXACTLY on the text returned by the tool. 
    3. DO NOT GUESS: If the exact steps or information are not in the tool's text, DO NOT make up your own instructions. 
    4. FALLBACK: If the answer is not in the retrieved data, politely state: "I couldn't find the exact information for that in our knowledge base. Please reach out to Tonik Bank customer support for further assistance."
    """)
    response = common_llm.invoke([prompt] + state["messages"])
    return {"messages": [response]}
