"""WebSocket routes for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
        self.conversation_subscribers: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and add a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.remove(websocket)
        
        # Remove from conversation subscribers
        for conv_id, subscribers in list(self.conversation_subscribers.items()):
            if websocket in subscribers:
                subscribers.remove(websocket)
                if not subscribers:
                    del self.conversation_subscribers[conv_id]
    
    async def subscribe_conversation(
        self,
        websocket: WebSocket,
        conversation_id: str
    ):
        """Subscribe to updates for a specific conversation."""
        if conversation_id not in self.conversation_subscribers:
            self.conversation_subscribers[conversation_id] = []
        self.conversation_subscribers[conversation_id].append(websocket)
    
    async def unsubscribe_conversation(
        self,
        websocket: WebSocket,
        conversation_id: str
    ):
        """Unsubscribe from conversation updates."""
        if conversation_id in self.conversation_subscribers:
            if websocket in self.conversation_subscribers[conversation_id]:
                self.conversation_subscribers[conversation_id].remove(websocket)
            if not self.conversation_subscribers[conversation_id]:
                del self.conversation_subscribers[conversation_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific connection."""
        try:
            await websocket.send_text(message)
        except Exception:
            # Connection might be closed
            pass
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    async def broadcast_to_conversation(
        self,
        conversation_id: str,
        message: dict
    ):
        """Broadcast message to all subscribers of a conversation."""
        if conversation_id not in self.conversation_subscribers:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.conversation_subscribers[conversation_id]:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            if connection in self.conversation_subscribers[conversation_id]:
                self.conversation_subscribers[conversation_id].remove(connection)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates.
    
    Clients can send commands:
    - {"action": "subscribe", "conversation_id": "..."}
    - {"action": "unsubscribe", "conversation_id": "..."}
    - {"action": "ping"}
    
    Server sends updates:
    - {"type": "new_message", "conversation_id": "...", "data": {...}}
    - {"type": "intelligence_extracted", "conversation_id": "...", "data": {...}}
    - {"type": "conversation_status", "conversation_id": "...", "status": "..."}
    - {"type": "analytics_update", "data": {...}}
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Agentic HoneyPot WebSocket"
        })
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle actions
                action = message.get("action")
                
                if action == "subscribe":
                    conversation_id = message.get("conversation_id")
                    if conversation_id:
                        await manager.subscribe_conversation(websocket, conversation_id)
                        await websocket.send_json({
                            "type": "subscribed",
                            "conversation_id": conversation_id
                        })
                
                elif action == "unsubscribe":
                    conversation_id = message.get("conversation_id")
                    if conversation_id:
                        await manager.unsubscribe_conversation(websocket, conversation_id)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "conversation_id": conversation_id
                        })
                
                elif action == "ping":
                    await websocket.send_json({"type": "pong"})
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


async def notify_new_message(conversation_id: str, message_data: dict):
    """Notify subscribers about a new message."""
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "type": "new_message",
            "conversation_id": conversation_id,
            "data": message_data
        }
    )


async def notify_intelligence_extracted(
    conversation_id: str,
    intelligence_data: dict
):
    """Notify about new intelligence extraction."""
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "type": "intelligence_extracted",
            "conversation_id": conversation_id,
            "data": intelligence_data
        }
    )
    
    # Also broadcast to all connections for dashboard update
    await manager.broadcast({
        "type": "analytics_update",
        "trigger": "intelligence_extracted"
    })


async def notify_conversation_status(conversation_id: str, status: str):
    """Notify about conversation status change."""
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "type": "conversation_status",
            "conversation_id": conversation_id,
            "status": status
        }
    )
    
    # Broadcast to all for dashboard update
    await manager.broadcast({
        "type": "analytics_update",
        "trigger": "conversation_status_change"
    })
