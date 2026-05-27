import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import get_storage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_create_task_success(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test description",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["owner_id"] == 10
    assert "id" in data

def test_create_task_invalid_title_length(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Te",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422

def test_create_task_no_auth_header(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "priority": 3
        }
    )
    assert response.status_code == 401

def test_user_sees_only_own_tasks(client):
    client.post("/tasks", json={"title": "Task1", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "Task2", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "Task3", "priority": 3}, headers={"X-User-Id": "20"})
    
    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2

def test_filter_tasks_by_status_and_priority(client):
    client.post("/tasks", json={"title": "Task1", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "Task2", "status": "done", "priority": 4}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "Task3", "status": "in_progress", "priority": 3}, headers={"X-User-Id": "10"})
    
    response = client.get("/tasks?status=done&min_priority=3", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"

def test_update_task_status_success(client):
    create_resp = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_access_foreign_task_returns_404(client):
    create_resp = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404

def test_delete_task_success(client):
    create_resp = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_response.status_code == 404
