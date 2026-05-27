from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class RoomManager:
    def __init__(self):
        self._rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        
        self._rooms[room_id][username] = websocket
        
        await self.broadcast(room_id, {
            "type": "user_joined",
            "room_id": room_id,
            "username": username
        })

    async def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        if room_id in self._rooms:
            if username in self._rooms[room_id]:
                del self._rooms[room_id][username]
                
                if len(self._rooms[room_id]) == 0:
                    del self._rooms[room_id]
                else:
                    await self.broadcast(room_id, {
                        "type": "user_left",
                        "room_id": room_id,
                        "username": username
                    })

    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self._rooms:
            for username, connection in self._rooms[room_id].items():
                try:
                    await connection.send_json(payload)
                except:
                    pass

    def get_users(self, room_id: str) -> list:
        if room_id in self._rooms:
            return list(self._rooms[room_id].keys())
        return []

_room_manager = RoomManager()

def get_room_manager():
    return _room_manager
