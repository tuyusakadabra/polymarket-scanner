from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class OutcomeToken:
    outcome: str
    token_id: str


@dataclass(slots=True)
class Market:
    market_id: str
    title: str
    slug: str
    end_date: Optional[datetime]
    active: bool
    volume: float
    outcomes: List[OutcomeToken] = field(default_factory=list)
    event_slug: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderBookTop:
    token_id: str
    bid: Optional[float]
    ask: Optional[float]
    bid_size: float
    ask_size: float
    midpoint: Optional[float]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParsedTitle:
    pattern: str
    underlying: Optional[str]
    direction: Optional[str]
    strike: Optional[float]
    strike2: Optional[float] = None
    maturity: Optional[datetime] = None


@dataclass(slots=True)
class Signal:
    signal_type: str
    market_title: str
    market_id: str
    edge: float
    score: float
    confidence: str
    liquidity: float
    spread_penalty: float
    notes: str
    token_ids: List[str] = field(default_factory=list)
    event_slug: Optional[str] = None
    end_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
