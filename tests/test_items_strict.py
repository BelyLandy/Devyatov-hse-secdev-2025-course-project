from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
H = {"X-User-Id": "u1"}


def test_extra_field_rejected():
    payload = {"title": "X", "impact": 5, "effort": 5, "hacker": "oops"}
    r = client.post("/api/v1/items", headers=H, json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["title"] == "Validation Error"
    errors = body.get("errors", [])
    assert any(
        (e.get("type") == "extra_forbidden")
        or ("extra inputs are not permitted" in (e.get("msg", "").lower()))
        or ("extra fields not permitted" in (e.get("msg", "").lower()))
        for e in errors
    )


def test_invalid_sort_literal():
    r = client.get("/api/v1/items?sort=hacked", headers=H)
    assert r.status_code == 422
