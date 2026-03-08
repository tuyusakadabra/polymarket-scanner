"""Risk limit checks."""


def check_notional_limits(
    market_notional: float,
    total_notional: float,
    max_notional_per_market: float,
    max_total_notional: float,
) -> tuple[bool, str]:
    """Return limit status and reason."""
    if market_notional > max_notional_per_market:
        return False, "max_notional_per_market"
    if total_notional > max_total_notional:
        return False, "max_total_notional"
    return True, "ok"
