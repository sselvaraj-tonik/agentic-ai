from typing import Annotated
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.builder import graph_executor
from app.config.logging import logger
from app.core.decorators import log_execution_time

class ChatResponse(BaseModel):
    response: str

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@log_execution_time
def chat_endpoint(
    query: Annotated[str, Form()],
    thread_id: Annotated[str, Form()] = "default_thread_1"
):
    try:
        # Pass the thread_id into the LangGraph config
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke with config
        result = graph_executor.invoke(
            {"messages": [HumanMessage(content=query)]},
            config=config
        )

        messages = result.get("messages", [])
        if not messages:
            return ChatResponse(response="No response generated.")

        last_message = messages[-1]
        return ChatResponse(response=last_message.content)

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
