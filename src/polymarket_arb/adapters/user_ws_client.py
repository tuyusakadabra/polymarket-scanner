"""User websocket adapter (disabled in V1 unless live trading feature enabled)."""

from collections.abc import AsyncIterator


class UserWSClient:
    """Stub for authenticated user-channel events."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    async def stream(self) -> AsyncIterator[dict]:
        """Yield no events when disabled; raises if unexpectedly enabled."""
        if self.enabled:
            raise RuntimeError("Live trading/user stream is disabled in V1")
        if False:  # pragma: no cover
            yield {}
