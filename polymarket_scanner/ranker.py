from __future__ import annotations

import math
from typing import List

from polymarket_scanner.models import Signal


CONFIDENCE_WEIGHT = {
    "HIGH": 1.0,
    "MED": 0.7,
    "LOW": 0.4,
}


def score_signal(signal: Signal) -> float:
    weight = CONFIDENCE_WEIGHT.get(signal.confidence, 0.5)
    liquidity_term = math.log1p(max(signal.liquidity, 0.0))
    score = signal.edge * weight * liquidity_term - signal.spread_penalty
    return score


def rank_signals(signals: List[Signal]) -> List[Signal]:
    for signal in signals:
        signal.score = score_signal(signal)
    return sorted(signals, key=lambda s: s.score, reverse=True)
