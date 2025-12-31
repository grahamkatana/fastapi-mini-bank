from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.exceptions import WebSocketException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.websocket import manager
from app.config import settings

router = APIRouter()


async def get_user_from_token(token: str, db: Session) -> User:
    """Validate WebSocket token and get user"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        
        return user
    except JWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for authenticated real-time updates
    
    Connect with: ws://localhost:8000/api/v1/ws?token=YOUR_JWT_TOKEN
    
    Receives real-time notifications for:
    - New transactions
    - Account balance updates
    - Login events
    - System notifications
    """
    # Validate token and get user
    try:
        user = await get_user_from_token(token, db)
    except WebSocketException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return
    
    # Connect user
    await manager.connect(websocket, user.id)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connection",
        "status": "connected",
        "message": f"Welcome {user.username}! You are now connected to real-time updates.",
        "user_id": user.id
    })
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "message": "Connection is alive"
                })
            else:
                # Handle other messages if needed
                await websocket.send_json({
                    "type": "echo",
                    "message": f"Received: {data}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
        print(f"User {user.id} disconnected")
    except Exception as e:
        print(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(websocket, user.id)


@router.websocket("/ws/public")
async def public_websocket_endpoint(websocket: WebSocket):
    """
    Public WebSocket endpoint for unauthenticated updates
    
    Connect with: ws://localhost:8000/api/v1/ws/public
    
    Receives:
    - System announcements
    - Public notifications
    """
    await manager.connect(websocket)
    
    await websocket.send_json({
        "type": "connection",
        "status": "connected",
        "message": "Connected to public updates"
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "message": "Connection is alive"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Public client disconnected")
    except Exception as e:
        print(f"Public WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ws/connections")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_active_connections_count(),
        "users_connected": len(manager.active_connections)
    }
