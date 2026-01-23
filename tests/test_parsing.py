from datetime import datetime

from polymarket_scanner.parsing import parse_title


def test_parse_threshold_above() -> None:
    parsed = parse_title("BTC above $100,000 on Dec 31, 2025")
    assert parsed.pattern == "THRESHOLD"
    assert parsed.underlying == "BTC"
    assert parsed.direction == "above"
    assert parsed.strike == 100000.0


def test_parse_range() -> None:
    parsed = parse_title("ETH between $1,500 and $2,000", end_date=datetime(2025, 1, 1))
    assert parsed.pattern == "RANGE"
    assert parsed.underlying == "ETH"
    assert parsed.strike == 1500.0
    assert parsed.strike2 == 2000.0
