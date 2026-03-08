"""Orderbook local state."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from polymarket_arb.models import BookLevel, OrderBookTop


@dataclass(slots=True)
class LocalOrderBook:
    """Maintains top-of-book for a token."""

    token_id: str
    bids: dict[float, float] = field(default_factory=dict)
    asks: dict[float, float] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def apply_update(self, bids: list[tuple[float, float]], asks: list[tuple[float, float]]) -> OrderBookTop:
        """Apply incremental absolute-size updates."""
        for price, size in bids:
            if size <= 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = size
        for price, size in asks:
            if size <= 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = size
        self.updated_at = datetime.now(timezone.utc)
        return self.top()

    def top(self) -> OrderBookTop:
        """Return top-of-book metrics."""
        best_bid_price = max(self.bids.keys()) if self.bids else None
        best_ask_price = min(self.asks.keys()) if self.asks else None
        best_bid = BookLevel(best_bid_price, self.bids[best_bid_price]) if best_bid_price is not None else None
        best_ask = BookLevel(best_ask_price, self.asks[best_ask_price]) if best_ask_price is not None else None
        midpoint = None
        spread = None
        if best_bid and best_ask:
            midpoint = (best_bid.price + best_ask.price) / 2
            spread = best_ask.price - best_bid.price
        return OrderBookTop(
            token_id=self.token_id,
            best_bid=best_bid,
            best_ask=best_ask,
            midpoint=midpoint,
            spread=spread,
            updated_at=self.updated_at,
        )
