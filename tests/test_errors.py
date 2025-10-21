# tests/test_errors.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert set(["type", "title", "status", "detail", "correlation_id"]).issubset(
        body.keys()
    )
    assert body["title"] == "Not Found"
    assert body["status"] == 404
    assert body["detail"]  # есть текстовое описание
    assert isinstance(body["correlation_id"], str) and len(body["correlation_id"]) > 0


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["title"] == "Validation Error"
    assert body["status"] == 422
    assert "errors" in body and isinstance(body["errors"], list)
    assert any("loc" in e for e in body["errors"])


def test_value_error_is_problem():
    from app.utils.rfc7807 import problem

    resp = problem(400, "Bad Request", "boom", type_="about:blank#value-error")
    body = resp.body
    assert b'"status":400' in body and b'"title":"Bad Request"' in body
