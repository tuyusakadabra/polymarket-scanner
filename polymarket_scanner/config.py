from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Config:
    gamma_base_url: str = "https://gamma-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"
    gamma_markets_path: str = "/markets"
    gamma_events_path: str = "/events"
    clob_orderbook_path: str = "/books/{token_id}"
    fee_rate_bps: float = 0.0
    safety_margin: float = 0.005
    epsilon_monotonicity: float = 0.01
    epsilon_range: float = 0.03
    cache_ttl_seconds: int = 15
    retry_attempts: int = 3
    retry_backoff_seconds: float = 0.7
    request_timeout_seconds: float = 10.0
    min_liquidity: float = 50.0
    min_volume: float = 0.0
    log_level: str = "INFO"

    def cost_margin(self) -> float:
        return self.safety_margin + (self.fee_rate_bps / 10_000.0)


@dataclass(slots=True)
class ScanOptions:
    query: Optional[str]
    top: int
    min_liquidity: float
    min_volume: float
    export_json: Optional[str]
    export_csv: Optional[str]
    event_slug: Optional[str] = None
