from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from polymarket_scanner.models import ParsedTitle

_THRESHOLD_PATTERNS = [
    re.compile(r"(?P<underlying>[A-Za-z0-9]+)\s+(?:above|over|greater than|>)\s+\$?(?P<strike>[\d,.]+)", re.IGNORECASE),
    re.compile(r"(?P<underlying>[A-Za-z0-9]+)\s+(?:below|under|less than|<)\s+\$?(?P<strike>[\d,.]+)", re.IGNORECASE),
]

_RANGE_PATTERN = re.compile(
    r"(?P<underlying>[A-Za-z0-9]+)\s+(?:between|in range)\s+\$?(?P<strike1>[\d,.]+)\s*(?:and|to|-)\s*\$?(?P<strike2>[\d,.]+)",
    re.IGNORECASE,
)


def _parse_number(value: str) -> Optional[float]:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def parse_title(title: str, end_date: Optional[datetime] = None) -> ParsedTitle:
    for pattern in _THRESHOLD_PATTERNS:
        match = pattern.search(title)
        if match:
            strike = _parse_number(match.group("strike"))
            direction = "above" if "above" in match.group(0).lower() or "over" in match.group(0).lower() or ">" in match.group(0) else "below"
            return ParsedTitle(
                pattern="THRESHOLD",
                underlying=match.group("underlying").upper(),
                direction=direction,
                strike=strike,
                maturity=end_date,
            )

    match_range = _RANGE_PATTERN.search(title)
    if match_range:
        strike1 = _parse_number(match_range.group("strike1"))
        strike2 = _parse_number(match_range.group("strike2"))
        return ParsedTitle(
            pattern="RANGE",
            underlying=match_range.group("underlying").upper(),
            direction=None,
            strike=strike1,
            strike2=strike2,
            maturity=end_date,
        )

    return ParsedTitle(pattern="UNKNOWN", underlying=None, direction=None, strike=None, maturity=end_date)
