from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi import status
from app.routers import tasks, users, admin
from app.websocket.room_manager import get_room_manager, RoomManager
from app.dependencies import get_current_user

app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    username: str = None
):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return
    
    username = username.strip()
    manager = get_room_manager()
    
    try:
        await manager.connect(room_id, username, websocket)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                text = data.get("text", "")
                
                if len(text) > 300:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long"
                    })
                else:
                    await manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    
    except WebSocketDisconnect:
        await manager.disconnect(room_id, username, websocket)

@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    manager = get_room_manager()
    return {"room_id": room_id, "users": manager.get_users(room_id)}
