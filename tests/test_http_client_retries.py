import httpx

from app.utils import http_client as hc


class DummyResp:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=None)

    def json(self):
        return self._body


class DummyClient:
    def __init__(self, sequence):
        self.sequence = list(sequence)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, headers=None):
        action = self.sequence.pop(0)
        if action == "timeout":
            raise httpx.TimeoutException("t/o")
        if action == "5xx":
            raise httpx.HTTPError("server err")
        return DummyResp(200, {"ok": True})


def test_get_json_retries_timeout(monkeypatch):
    seq = ["timeout", "ok"]
    monkeypatch.setattr(hc, "client", lambda: DummyClient(seq))
    data = hc.get_json("http://example.com", max_retries=2, backoff=0.01)
    assert data == {"ok": True}


def test_get_json_retries_http_error(monkeypatch):
    seq = ["5xx", "ok"]
    monkeypatch.setattr(hc, "client", lambda: DummyClient(seq))
    data = hc.get_json("http://example.com", max_retries=2, backoff=0.01)
    assert data == {"ok": True}


def test_get_json_fails_after_retries(monkeypatch):
    seq = ["timeout", "timeout", "timeout"]
    monkeypatch.setattr(hc, "client", lambda: DummyClient(seq))
    try:
        hc.get_json("http://example.com", max_retries=2, backoff=0.01)
        assert False, "Expected final exception"
    except httpx.TimeoutException:
        pass
