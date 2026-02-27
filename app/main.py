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
def chat_endpoint(
    query: Annotated[str, Form()],
    thread_id: Annotated[str, Form()] = "default_thread_1" # <--- ADD THREAD ID
):
    try:
        # Pass the thread_id into the LangGraph config
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke with config
        result = agent_executor.invoke(
            {"messages": [HumanMessage(content=query)]},
            config=config
        )

        messages = result.get("messages", [])
        if not messages:
            return ChatResponse(response="No response generated.")

        last_message = messages[-1]
        return ChatResponse(response=last_message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
