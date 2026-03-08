"""Backtest reporting helpers."""


def summarize_pnl(realized: float, unrealized: float) -> dict[str, float]:
    """Return basic PnL summary."""
    return {"realized": realized, "unrealized": unrealized, "total": realized + unrealized}
