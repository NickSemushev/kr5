import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import get_storage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
