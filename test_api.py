from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() ==  {"message": "Hello World"}

def test_get_batches():
    response = client.get("/batches/db")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "batches" in data