from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime
import json


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store all connections for broadcast
        self.all_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.all_connections.add(websocket)
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove a WebSocket connection"""
        self.all_connections.discard(websocket)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user's connections"""
        if user_id in self.active_connections:
            message_data = self._format_message(message)
            disconnected = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message_data)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        message_data = self._format_message(message)
        disconnected = []
        
        for connection in self.all_connections.copy():
            try:
                await connection.send_json(message_data)
            except Exception as e:
                print(f"Error broadcasting: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.all_connections.discard(conn)
    
    def _format_message(self, message: dict) -> dict:
        """Format message with timestamp"""
        return {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_active_connections_count(self, user_id: int = None) -> int:
        """Get count of active connections"""
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return len(self.all_connections)


# Global connection manager instance
manager = ConnectionManager()
