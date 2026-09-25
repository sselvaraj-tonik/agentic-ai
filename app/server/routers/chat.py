from typing import Annotated
from fastapi import APIRouter, HTTPException, Form, Request, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.builder import graph_executor
from app.config.logging import logger
from app.core.decorators import async_log_execution_time
from app.core.security import mask_pii
from app.core.tracing import resolve_trace_id, get_trace_id
import time
import asyncio
import traceback
import json
from app.server.websocket_manager import manager

class ChatResponse(BaseModel):
    response: str
    latency_ms: float

router = APIRouter()

# ---------------------------------------------------------
# SHARED CORE LOGIC
# ---------------------------------------------------------
async def process_chat_message(query: str, thread_id: str, trace_id: str) -> tuple[str, float]:
    """Shared core logic for executing the LangGraph pipeline."""
    start_time = time.time()

    # Mask input query for logging
    masked_query = mask_pii(query)
    logger.info(f"Processing chat request: thread_id={thread_id}, query={masked_query}, trace_id={trace_id}")

    try:
        # Pass the thread_id into the LangGraph config
        config = {"configurable": {"thread_id": thread_id}}

        # In a real async environment, we use ainvoke to avoid blocking
        result = await graph_executor.ainvoke(
            {"messages": [HumanMessage(content=query)], "trace_id": trace_id},
            config=config
        )

        messages = result.get("messages", [])
        if not messages:
            return "No response generated.", (time.time() - start_time) * 1000

        last_message = messages[-1]
        response_text = last_message.content if isinstance(last_message.content, str) else str(last_message.content)

        # Guard against degenerate LLM outputs
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

        latency = (time.time() - start_time) * 1000
        logger.info(f"Chat request completed in {latency:.2f}ms for trace_id={trace_id}")
        return response_text, latency

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Chat execution error for thread_id={thread_id}, trace_id={trace_id}: {str(e)}")
        logger.error(f"Full Traceback: {error_details}")
        raise e  # Bubble up to the router handlers


# ---------------------------------------------------------
# HTTP REST ENDPOINT
# ---------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
@async_log_execution_time
async def chat_endpoint(
    request: Request,
    response: Response,
    query: Annotated[str, Form()],
    thread_id: Annotated[str, Form()] = "default_thread_1"
):
    incoming = request.headers.get("X-Trace-Id") or request.headers.get("X-Request-Id")
    trace_id = resolve_trace_id(incoming)
    response.headers["X-Trace-Id"] = trace_id

    try:
        response_text, latency = await process_chat_message(query, thread_id, trace_id)
        return ChatResponse(
            response=response_text,
            latency_ms=latency
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request. Please try again later."
        )


# ---------------------------------------------------------
# WEBSOCKET ENDPOINT
# ---------------------------------------------------------
@router.websocket("/ws/chat/{thread_id}")
async def chat_websocket(websocket: WebSocket, thread_id: str):
    await manager.connect(websocket, thread_id)
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                
                # Check for ping/pong heartbeat
                msg_type = payload.get("type")
                if msg_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
                    continue
                elif msg_type == "init_session":
                    # Handle init_session payload
                    logger.info(f"Initialized session for thread {thread_id} with data {payload.get('user', {})}")
                    await manager.send_personal_message({
                        "type": "system_status",
                        "status": "ready"
                    }, websocket)
                    continue

                query = payload.get("text", "")
                incoming_trace = payload.get("trace_id")
            except json.JSONDecodeError:
                query = data.strip()
                incoming_trace = None

            if not query:
                continue

            trace_id = resolve_trace_id(incoming_trace)

            # Send typing indicator while processing
            await manager.broadcast_to_thread({
                "type": "typing_indicator",
                "status": "typing"
            }, thread_id)

            try:
                # Process the message using the shared graph executor
                response_text, latency = await process_chat_message(query, thread_id, trace_id)
                
                # Broadcast the response back to all clients connected to this thread
                await manager.broadcast_to_thread({
                    "type": "chat_response",
                    "text": response_text,
                    "latency_ms": latency,
                    "trace_id": trace_id,
                    "status": "success"
                }, thread_id)

            except Exception as e:
                logger.error(f"Error processing message for thread {thread_id}: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "error": "An internal error occurred while processing your request.",
                    "trace_id": trace_id,
                    "status": "error"
                }, websocket)

            finally:
                # Clear typing indicator
                await manager.broadcast_to_thread({
                    "type": "typing_indicator",
                    "status": "idle"
                }, thread_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)
    except Exception as e:
        logger.error(f"Unexpected WebSocket error for thread_id={thread_id}: {str(e)}")
        manager.disconnect(websocket, thread_id)
        # Attempt to close the websocket gracefully if not already closed
        try:
            await websocket.close()
        except Exception:
            pass