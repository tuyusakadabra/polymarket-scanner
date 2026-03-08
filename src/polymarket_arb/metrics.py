"""In-memory counters for lightweight observability."""

from collections import defaultdict


class Metrics:
    """Simple metric collector for counters and gauges."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = defaultdict(int)
        self.gauges: dict[str, float] = {}

    def inc(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value
