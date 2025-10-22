# app/utils/http_client.py
from typing import Optional

import httpx

DEFAULT_CONNECT = 2.0
DEFAULT_READ = 3.0
DEFAULT_TOTAL = 5.0


def client(timeout_total: float = DEFAULT_TOTAL) -> httpx.Client:
    timeout = httpx.Timeout(timeout_total, connect=DEFAULT_CONNECT, read=DEFAULT_READ)
    return httpx.Client(timeout=timeout)


def get_json(url: str, headers: Optional[dict] = None):
    try:
        with client() as c:
            r = c.get(url, headers=headers)
            r.raise_for_status()
            return r.json()
    except httpx.TimeoutException:
        raise
    except httpx.HTTPError:
        raise
