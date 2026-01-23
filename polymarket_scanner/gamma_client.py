from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from polymarket_scanner.config import Config
from polymarket_scanner.models import Market, OutcomeToken
from polymarket_scanner.utils import TTLCache, cached_json, request_json

logger = logging.getLogger(__name__)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        logger.debug("Unable to parse datetime: %s", value)
        return None


class GammaClient:
    def __init__(self, config: Config, cache: TTLCache) -> None:
        self.config = config
        self.cache = cache

    def fetch_markets(
        self,
        query: Optional[str],
        limit: int,
        min_volume: float,
        event_slug: Optional[str] = None,
    ) -> List[Market]:
        params: Dict[str, Any] = {
            "limit": limit,
        }
        if query:
            params["query"] = query
        if event_slug:
            params["event_slug"] = event_slug
        url = f"{self.config.gamma_base_url}{self.config.gamma_markets_path}"
        cache_key = f"gamma_markets:{query}:{limit}:{min_volume}:{event_slug}"

        def _fetch() -> tuple[Optional[Any], Optional[Exception]]:
            return request_json(
                url,
                params=params,
                timeout_seconds=self.config.request_timeout_seconds,
                retries=self.config.retry_attempts,
                backoff_seconds=self.config.retry_backoff_seconds,
            )

        payload, error = cached_json(self.cache, cache_key, _fetch)
        if error or payload is None:
            logger.error("Gamma markets fetch failed: %s", error)
            return []

        markets_data = payload if isinstance(payload, list) else payload.get("markets", [])
        markets: List[Market] = []
        for item in markets_data:
            volume = float(item.get("volume", 0) or 0)
            if volume < min_volume:
                continue
            outcomes = []
            for outcome, token_id in zip(item.get("outcomes", []), item.get("token_ids", [])):
                if not token_id:
                    continue
                outcomes.append(OutcomeToken(outcome=str(outcome), token_id=str(token_id)))
            market = Market(
                market_id=str(item.get("id") or item.get("market_id") or item.get("slug") or ""),
                title=str(item.get("title") or item.get("question") or "Unknown"),
                slug=str(item.get("slug") or ""),
                end_date=_parse_datetime(item.get("end_date") or item.get("close_time")),
                active=bool(item.get("active", True)),
                volume=volume,
                outcomes=outcomes,
                event_slug=item.get("event_slug"),
                url=item.get("url"),
                metadata=item,
            )
            markets.append(market)
        return markets
