from langchain_core.messages import SystemMessage
from app.core.state import AgentState, RouteResponse
from app.core.llm import get_llm
from app.config.logging import logger

# Production-grade prompt with Capability Mapping and Few-Shot Examples
SUPERVISOR_PROMPT = """You are an expert banking routing supervisor.
Analyze the user's request and the conversation history. Route the user to the specialized department that possesses the exact tools needed to fulfill their request.

DEPARTMENT CAPABILITIES:

1. 'accounts_agent'
   - Tools available: [get_customer_profile, search_payee, execute_transfer]
   - Description: Handles inquiries about the user's identity, general profile, account status, and the movement of funds / executing transfers.

2. 'common_agent'
   - Tools available: []
   - Description: Handles general banking questions, FAQs, and common inquiries not related to specific accounts or loans.

3. 'loans_agent'
   - Tools available: [check_loan_status, process_loan_payment]
   - Description: Handles all inquiries and payments specifically tied to loans and EMIs.

4. 'FINISH'
   - Use this if the user is just saying hello, or if the active task has been successfully completed and no further action is requested.

EXAMPLES:
User: "Send 10k to Xavier."
Decision: accounts_agent

User: "How much is my EMI this month?"
Decision: loans_agent

User: "Get my profile details for 631234567890."
Decision: accounts_agent

User: "Thank you, that's all I needed."
Decision: FINISH
"""

def supervisor_node(state: AgentState):
    llm = get_llm()
    try:
        # Force the LLM to output valid JSON matching the RouteResponse schema
        router = llm.with_structured_output(RouteResponse)
        messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
        decision = router.invoke(messages)
        return {"next_node": decision.next_node}
    except Exception as e:
        # Fallback in case of an LLM or connection error
        logger.error(f"Supervisor routing error: {e}")
        return {"next_node": "FINISH"}

def route_supervisor(state: AgentState):
    """Routes from the supervisor to the specific agent, or ends the graph."""
    if state.get("next_node") == "FINISH":
        from langgraph.graph import END
        return END
    return state["next_node"]
