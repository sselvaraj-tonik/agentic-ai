from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, Request
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.builder import graph_executor
from app.config.logging import logger
from app.core.decorators import async_log_execution_time
from app.core.security import mask_pii
import time
import asyncio

class ChatResponse(BaseModel):
    response: str
    latency_ms: float

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@async_log_execution_time
async def chat_endpoint(
    request: Request,
    query: Annotated[str, Form()],
    thread_id: Annotated[str, Form()] = "default_thread_1"
):
    start_time = time.time()
    # Mask input query for logging
    masked_query = mask_pii(query)
    logger.info(f"Received chat request: thread_id={thread_id}, query={masked_query}")

    try:
        # Pass the thread_id into the LangGraph config
        config = {"configurable": {"thread_id": thread_id}}
        
        # In a real async environment, we should use ainvoke to avoid blocking
        # LangGraph supports ainvoke
        result = await graph_executor.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config=config
        )

        messages = result.get("messages", [])
        if not messages:
            return ChatResponse(
                response="No response generated.",
                latency_ms=(time.time() - start_time) * 1000
            )

        last_message = messages[-1]
        latency = (time.time() - start_time) * 1000

        logger.info(f"Chat request completed in {latency:.2f}ms")

        return ChatResponse(
            response=last_message.content,
            latency_ms=latency
        )

    except Exception as e:
        logger.error(f"Chat endpoint error for thread_id={thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing your request.")
