from typing import Annotated
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent import agent_executor
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI(
    title="Banking Agent AI",
    description="An Open Source Agentic AI for Banking Customer Support",
    version="1.1.0"
)

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(query: Annotated[str, Form()]):
    """
    Endpoint to interact with the Banking Agent.
    Accepts a 'query' form field (multipart/form-data or application/x-www-form-urlencoded).

    Example curl:
      curl -X POST http://localhost:8000/chat -F "query=Hello"
    """
    try:
        # Create the initial state with the user's message
        initial_state = {"messages": [HumanMessage(content=query)]}

        # Run the agent
        result = agent_executor.invoke(initial_state)

        # Extract the final message from the conversation history
        messages = result.get("messages", [])
        if not messages:
            return ChatResponse(response="No response generated.")

        last_message = messages[-1]

        return ChatResponse(response=last_message.content)

    except Exception as e:
        # Log the error in a real app
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
