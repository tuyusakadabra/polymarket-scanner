from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from polymarket_scanner.config import Config
from polymarket_scanner.models import OrderBookTop
from polymarket_scanner.utils import TTLCache, cached_json, request_json

logger = logging.getLogger(__name__)


class ClobClient:
    def __init__(self, config: Config, cache: TTLCache) -> None:
        self.config = config
        self.cache = cache

    def _orderbook_url(self, token_id: str) -> str:
        path = self.config.clob_orderbook_path.format(token_id=token_id)
        return f"{self.config.clob_base_url}{path}"

    def fetch_orderbook_top(self, token_id: str) -> Optional[OrderBookTop]:
        url = self._orderbook_url(token_id)
        cache_key = f"clob_orderbook:{token_id}"

        def _fetch() -> tuple[Optional[Any], Optional[Exception]]:
            return request_json(
                url,
                timeout_seconds=self.config.request_timeout_seconds,
                retries=self.config.retry_attempts,
                backoff_seconds=self.config.retry_backoff_seconds,
            )

        payload, error = cached_json(self.cache, cache_key, _fetch)
        if error or payload is None:
            logger.debug("Orderbook fetch failed for %s: %s", token_id, error)
            return None

        bids = payload.get("bids") or payload.get("book", {}).get("bids") or []
        asks = payload.get("asks") or payload.get("book", {}).get("asks") or []

        top_bid = bids[0] if bids else None
        top_ask = asks[0] if asks else None

        def _parse_level(level: Any) -> tuple[Optional[float], float]:
            if not level:
                return None, 0.0
            price = float(level.get("price") or level.get("px") or 0)
            size = float(level.get("size") or level.get("quantity") or level.get("qty") or 0)
            return price if price > 0 else None, size

        bid, bid_size = _parse_level(top_bid)
        ask, ask_size = _parse_level(top_ask)
        midpoint = None
        if bid is not None and ask is not None:
            midpoint = (bid + ask) / 2.0

        return OrderBookTop(
            token_id=token_id,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
            midpoint=midpoint,
            raw=payload,
        )
