"""Paper execution simulation."""

from dataclasses import dataclass

from polymarket_arb.models import OrderBookTop
from polymarket_arb.state.inventory import Inventory


@dataclass(slots=True)
class FillDecision:
    """Result of simulated execution attempt."""

    filled: bool
    fill_price: float | None
    fill_size: float
    reason: str


class PaperExecutor:
    """Simulate taker and maker fills."""

    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory

    def simulate_taker(self, side: str, size: float, top: OrderBookTop) -> FillDecision:
        """Cross spread immediately in taker mode."""
        if side == "buy" and top.best_ask:
            return FillDecision(True, top.best_ask.price, size, "cross_ask")
        if side == "sell" and top.best_bid:
            return FillDecision(True, top.best_bid.price, size, "cross_bid")
        return FillDecision(False, None, 0.0, "no_liquidity")

    def simulate_maker(self, side: str, size: float, quote_price: float, top: OrderBookTop, queue_ahead: float = 1.0) -> FillDecision:
        """Conservative queue-aware maker fill model."""
        if side == "buy":
            if top.best_ask and quote_price >= top.best_ask.price and queue_ahead <= 1.0:
                return FillDecision(True, quote_price, size, "maker_hit")
        else:
            if top.best_bid and quote_price <= top.best_bid.price and queue_ahead <= 1.0:
                return FillDecision(True, quote_price, size, "maker_hit")
        return FillDecision(False, None, 0.0, "resting")
