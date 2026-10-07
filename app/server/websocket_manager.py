from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps thread_id to a list of active WebSocket connections
        # This allows multiple tabs/devices for the same user session
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)
        logger.info(f"Client connected to thread {thread_id}. Active connections: {len(self.active_connections[thread_id])}")

    def disconnect(self, websocket: WebSocket, thread_id: str):
        if thread_id in self.active_connections:
            if websocket in self.active_connections[thread_id]:
                self.active_connections[thread_id].remove(websocket)
            
            # Clean up empty threads
            if not self.active_connections[thread_id]:
                del self.active_connections[thread_id]
        logger.info(f"Client disconnected from thread {thread_id}.")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_thread(self, message: dict, thread_id: str):
        if thread_id in self.active_connections:
            # We iterate over a copy of the list to handle potential removals during iteration
            for connection in self.active_connections[thread_id].copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to connection on thread {thread_id}: {e}")
                    self.disconnect(connection, thread_id)

    def is_connected(self, thread_id: str) -> bool:
        return thread_id in self.active_connections and len(self.active_connections[thread_id]) > 0

# Singleton instance
manager = ConnectionManager()
