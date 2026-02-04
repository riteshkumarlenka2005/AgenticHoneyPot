"""WebSocket routes for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.conversation_subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        
        # Remove from conversation subscriptions
        for conv_id in list(self.conversation_subscribers.keys()):
            self.conversation_subscribers[conv_id].discard(websocket)
            if not self.conversation_subscribers[conv_id]:
                del self.conversation_subscribers[conv_id]
    
    async def subscribe_to_conversation(
        self,
        websocket: WebSocket,
        conversation_id: str
    ):
        """Subscribe a connection to conversation updates."""
        if conversation_id not in self.conversation_subscribers:
            self.conversation_subscribers[conversation_id] = set()
        self.conversation_subscribers[conversation_id].add(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_conversation(
        self,
        conversation_id: str,
        message: dict
    ):
        """Send message to all subscribers of a conversation."""
        if conversation_id not in self.conversation_subscribers:
            return
        
        disconnected = set()
        subscribers = self.conversation_subscribers[conversation_id]
        
        for connection in subscribers:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_personal_message(
        self,
        message: dict,
        websocket: WebSocket
    ):
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates.
    
    Clients can subscribe to:
    - All system events
    - Specific conversation updates
    
    Message format (client -> server):
    {
        "type": "subscribe",
        "conversation_id": "uuid"
    }
    
    Message format (server -> client):
    {
        "type": "new_message" | "conversation_update" | "intelligence_extracted",
        "data": {...}
    }
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to HoneyPot WebSocket",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle subscription requests
            if data.get("type") == "subscribe":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    await manager.subscribe_to_conversation(
                        websocket,
                        conversation_id
                    )
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
            
            elif data.get("type") == "ping":
                # Respond to ping
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_new_message(conversation_id: str, message: dict):
    """Broadcast new message event to subscribers."""
    await manager.send_to_conversation(conversation_id, {
        "type": "new_message",
        "conversation_id": conversation_id,
        "data": message,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_intelligence_extracted(
    conversation_id: str,
    intelligence: dict
):
    """Broadcast intelligence extraction event."""
    await manager.send_to_conversation(conversation_id, {
        "type": "intelligence_extracted",
        "conversation_id": conversation_id,
        "data": intelligence,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_conversation_update(
    conversation_id: str,
    update: dict
):
    """Broadcast conversation status update."""
    await manager.send_to_conversation(conversation_id, {
        "type": "conversation_update",
        "conversation_id": conversation_id,
        "data": update,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_system_event(event_type: str, data: dict):
    """Broadcast system-wide event to all connections."""
    await manager.broadcast({
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })
