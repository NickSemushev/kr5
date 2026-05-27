import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from app.main import app
from app.storage import get_storage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_websocket_connect_valid_username(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        pass

def test_websocket_connect_no_username(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/rooms/test"):
            pass

def test_websocket_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        websocket.send_json({"type": "message", "text": "Hello"})
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["room_id"] == "test"
        assert response["username"] == "alice"
        assert response["text"] == "Hello"

def test_two_clients_same_room_receive_message(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as ws1:
        with client.websocket_connect("/ws/rooms/test?username=bob") as ws2:
            ws1.send_json({"type": "message", "text": "Hello everyone"})
            
            response1 = ws1.receive_json()
            response2 = ws2.receive_json()
            
            assert response1["text"] == "Hello everyone"
            assert response2["text"] == "Hello everyone"

def test_different_rooms_no_cross_talk(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1:
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            ws1.send_json({"type": "message", "text": "Message in room1"})
            
            response1 = ws1.receive_json()
            assert response1["text"] == "Message in room1"
            
            with pytest.raises(Exception):
                ws2.receive_json(timeout=0.1)

def test_message_too_long_returns_error(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        long_text = "x" * 301
        websocket.send_json({"type": "message", "text": long_text})
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["detail"] == "Message is too long"

def test_user_removed_from_room_after_disconnect(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        response = client.get("/rooms/test/users")
        assert response.json()["users"] == ["alice"]
    
    response = client.get("/rooms/test/users")
    assert response.json()["users"] == []
