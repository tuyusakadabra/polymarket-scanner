from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() > entry.expires_at:
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + self.ttl_seconds)


def request_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout_seconds: float = 10.0,
    retries: int = 3,
    backoff_seconds: float = 0.5,
) -> Tuple[Optional[Any], Optional[Exception]]:
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
            return response.json(), None
        except Exception as exc:  # noqa: BLE001 - surface for logging
            last_error = exc
            logger.warning("Request failed (%s/%s): %s", attempt, retries, exc)
            if attempt < retries:
                time.sleep(backoff_seconds * attempt)
    return None, last_error


def cached_json(
    cache: TTLCache,
    cache_key: str,
    fetcher: Callable[[], Tuple[Optional[Any], Optional[Exception]]],
) -> Tuple[Optional[Any], Optional[Exception]]:
    cached = cache.get(cache_key)
    if cached is not None:
        return cached, None
    data, error = fetcher()
    if error is None and data is not None:
        cache.set(cache_key, data)
    return data, error
