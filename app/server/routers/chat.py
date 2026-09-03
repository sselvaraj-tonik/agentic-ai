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
        response_text = last_message.content if isinstance(last_message.content, str) else str(last_message.content)
        latency = (time.time() - start_time) * 1000

        # Guard against degenerate LLM outputs: an empty turn, or one that just
        # parrots the user's query back verbatim (a known failure mode of smaller
        # local models). Surface a safe fallback instead of the garbled reply.
        normalized_response = response_text.strip()
        if not normalized_response or normalized_response.lower() == query.strip().lower():
            logger.warning(
                f"Degenerate model response for thread_id={thread_id} "
                f"(empty or echoed query); returning fallback."
            )
            response_text = (
                "I'm sorry, I wasn't able to process that properly. "
                "Could you please rephrase your question?"
            )

        logger.info(f"Chat request completed in {latency:.2f}ms")

        return ChatResponse(
            response=response_text,
            latency_ms=latency
        )

    except Exception as e:
        import traceback
        # Capture the full stack trace as a string
        error_details = traceback.format_exc()
        logger.error(f"Chat endpoint error for thread_id={thread_id}: {str(e)}")
        logger.error(f"Full Traceback: {error_details}")

        # Return a generic message to the client; details stay in the server logs.
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request. Please try again later."
        )