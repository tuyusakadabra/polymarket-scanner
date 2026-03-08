"""Simple fair value tools."""


def midpoint_fair_value(best_bid: float | None, best_ask: float | None) -> float | None:
    """Use midpoint as baseline fair value when both sides are present."""
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2
