"""Domain models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class Market:
    """Normalized market metadata."""

    slug: str
    condition_id: str | None
    question: str
    category: str | None
    end_date: datetime | None
    liquidity: float
    token_ids: list[str]


@dataclass(slots=True)
class BookLevel:
    """Order book level."""

    price: float
    size: float


@dataclass(slots=True)
class OrderBookTop:
    """Top-of-book snapshot."""

    token_id: str
    best_bid: BookLevel | None = None
    best_ask: BookLevel | None = None
    midpoint: float | None = None
    spread: float | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Signal:
    """Signal emitted by scanner."""

    signal_type: str
    market_slug: str
    token_id: str
    raw_edge_bps: float
    net_edge_bps: float
    details: dict[str, str | float]
