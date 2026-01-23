from datetime import datetime

from polymarket_scanner.config import Config
from polymarket_scanner.models import Market, OrderBookTop, OutcomeToken
from polymarket_scanner.signals_noarb import detect_binary_complement, detect_monotonicity


def test_binary_complement_signal() -> None:
    market = Market(
        market_id="1",
        title="Test Market",
        slug="test",
        end_date=datetime(2025, 1, 1),
        active=True,
        volume=1000,
        outcomes=[
            OutcomeToken(outcome="YES", token_id="yes"),
            OutcomeToken(outcome="NO", token_id="no"),
        ],
    )
    books = {
        "yes": OrderBookTop(token_id="yes", bid=0.4, ask=0.45, bid_size=10, ask_size=10, midpoint=0.425),
        "no": OrderBookTop(token_id="no", bid=0.4, ask=0.45, bid_size=12, ask_size=12, midpoint=0.425),
    }
    signals = detect_binary_complement([market], books, Config(safety_margin=0.01))
    assert signals
    assert signals[0].signal_type == "arb_buy_both"


def test_monotonicity_violation() -> None:
    config = Config(epsilon_monotonicity=0.01)
    market_low = Market(
        market_id="low",
        title="BTC above $50,000",
        slug="btc-50k",
        end_date=datetime(2025, 1, 1),
        active=True,
        volume=1000,
        outcomes=[OutcomeToken(outcome="YES", token_id="yes-low")],
    )
    market_high = Market(
        market_id="high",
        title="BTC above $100,000",
        slug="btc-100k",
        end_date=datetime(2025, 1, 1),
        active=True,
        volume=1000,
        outcomes=[OutcomeToken(outcome="YES", token_id="yes-high")],
    )
    books = {
        "yes-low": OrderBookTop(token_id="yes-low", bid=0.4, ask=0.45, bid_size=10, ask_size=10, midpoint=0.425),
        "yes-high": OrderBookTop(token_id="yes-high", bid=0.5, ask=0.55, bid_size=10, ask_size=10, midpoint=0.525),
    }
    signals = detect_monotonicity([market_low, market_high], books, config)
    assert signals
    assert signals[0].signal_type == "monotonicity_violation"
