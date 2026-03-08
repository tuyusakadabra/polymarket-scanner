"""Kill switch checks."""


def check_kill_switch(drawdown: float, max_drawdown: float, stale_seconds: float, stale_timeout_seconds: int) -> tuple[bool, str]:
    """Return whether trading actions are allowed."""
    if drawdown >= max_drawdown:
        return False, "drawdown_limit"
    if stale_seconds >= stale_timeout_seconds:
        return False, "stale_data"
    return True, "ok"
