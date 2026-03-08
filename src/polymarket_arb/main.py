"""Main app composition helpers."""

from polymarket_arb.config import Settings
from polymarket_arb.logging import configure_logging


def bootstrap(settings: Settings) -> None:
    """Initialize runtime side effects like logging."""
    configure_logging(settings.log_level, settings.log_json)
