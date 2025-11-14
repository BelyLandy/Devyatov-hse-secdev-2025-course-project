import time
from typing import Optional

import httpx

DEFAULT_CONNECT = 2.0
DEFAULT_READ = 3.0
DEFAULT_TOTAL = 5.0


def client(timeout_total: float = DEFAULT_TOTAL) -> httpx.Client:
    """HTTPX client with sane timeouts."""
    timeout = httpx.Timeout(timeout_total, connect=DEFAULT_CONNECT, read=DEFAULT_READ)
    return httpx.Client(timeout=timeout, follow_redirects=True)


def get_json(
    url: str,
    headers: Optional[dict] = None,
    *,
    max_retries: int = 2,
    backoff: float = 0.25,
):
    """
    Safe JSON GET with timeouts + bounded retries + exponential backoff.
    Retries on httpx.TimeoutException / httpx.HTTPError (сетевые/5xx).
    """
    c = client()
    try:
        for attempt in range(max_retries + 1):
            try:
                r = c.get(url, headers=headers)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if not isinstance(e, (httpx.TimeoutException, httpx.HTTPError)):
                    raise
                if attempt == max_retries:
                    raise
                time.sleep(backoff * (2**attempt))
        raise RuntimeError("unreachable")
    finally:
        try:
            c.close()
        except Exception:
            pass
