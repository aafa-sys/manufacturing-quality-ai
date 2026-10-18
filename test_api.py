from fastapi.testclient import TestClient
from api import app
import os

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


def test_wrong_api_key():
    response = client.post(
        "/input-batch",
        headers={"X-API-Key": "wrong_key_123"},
        json={
            "batch_no": "TEST",
            "product_code": "PC-001",
            "product_name": "Test",
            "shift": "Shift 1",
            "manufacturing_line": "Line A",
            "plan_qty": 100
        }
    )
    assert response.status_code == 401

def test_missing_fields():
    api_key = os.getenv("API_KEY")
    response = client.post(
        "/input-batch",
        headers={"X-API-Key": api_key},
        json={"batch_no": "TEST"}     # cuma 1 field, harusnya 6
    )
    assert response.status_code == 422

def test_batch_not_found():
    response = client.get("/batch/NOTEXIST999")
    assert response.status_code == 404