from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
H = {"X-User-Id": "u1"}


def test_limit_too_big():
    r = client.get("/api/v1/items?limit=101", headers=H)
    assert r.status_code == 422


def test_negative_offset():
    r = client.get("/api/v1/items?offset=-1", headers=H)
    assert r.status_code == 422
