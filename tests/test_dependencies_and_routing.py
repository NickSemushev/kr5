import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import get_storage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"

def test_users_me_no_header_returns_401(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_regular_user_cannot_access_admin_stats(client):
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403

def test_admin_can_access_stats(client):
    client.post("/tasks", json={"title": "Task1", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10", "X-User-Role": "admin"})
    client.post("/tasks", json={"title": "Task2", "priority": 4, "status": "done"}, headers={"X-User-Id": "20", "X-User-Role": "admin"})
    
    response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 2
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["done"] == 1

def test_regular_user_cannot_delete_foreign_task(client):
    create_resp = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10", "X-User-Role": "user"})
    task_id = create_resp.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20", "X-User-Role": "user"})
    assert response.status_code == 404

def test_admin_can_delete_any_task_via_admin_endpoint(client):
    create_resp = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10", "X-User-Role": "user"})
    task_id = create_resp.json()["id"]
    
    response = client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert get_response.status_code == 404
