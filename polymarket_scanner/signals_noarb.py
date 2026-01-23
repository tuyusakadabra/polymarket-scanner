from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from polymarket_scanner.config import Config
from polymarket_scanner.models import Market, OrderBookTop, Signal
from polymarket_scanner.parsing import parse_title


def _spread_penalty(orderbook: OrderBookTop) -> float:
    if orderbook.bid is None or orderbook.ask is None:
        return 0.0
    return max(orderbook.ask - orderbook.bid, 0.0)


def _confidence(level: str) -> str:
    return level


def detect_binary_complement(
    markets: Iterable[Market],
    books: Dict[str, OrderBookTop],
    config: Config,
) -> List[Signal]:
    signals: List[Signal] = []
    for market in markets:
        if len(market.outcomes) != 2:
            continue
        token_yes, token_no = market.outcomes[0], market.outcomes[1]
        book_yes = books.get(token_yes.token_id)
        book_no = books.get(token_no.token_id)
        if not book_yes or not book_no:
            continue
        if book_yes.ask is None or book_no.ask is None:
            continue
        ask_sum = book_yes.ask + book_no.ask
        edge = 1.0 - ask_sum
        if edge <= config.cost_margin():
            continue
        liquidity = min(book_yes.ask_size, book_no.ask_size)
        spread_penalty = _spread_penalty(book_yes) + _spread_penalty(book_no)
        signals.append(
            Signal(
                signal_type="arb_buy_both",
                market_title=market.title,
                market_id=market.market_id,
                edge=edge,
                score=0.0,
                confidence=_confidence("HIGH"),
                liquidity=liquidity,
                spread_penalty=spread_penalty,
                notes=f"ask_yes={book_yes.ask:.4f}, ask_no={book_no.ask:.4f}",
                token_ids=[token_yes.token_id, token_no.token_id],
                event_slug=market.event_slug,
                end_date=market.end_date,
            )
        )
    return signals


def detect_multi_noarb(
    markets: Iterable[Market],
    books: Dict[str, OrderBookTop],
    config: Config,
) -> List[Signal]:
    signals: List[Signal] = []
    for market in markets:
        if len(market.outcomes) <= 2:
            continue
        ask_sum = 0.0
        liquidity = float("inf")
        spread_penalty = 0.0
        missing = False
        for outcome in market.outcomes:
            book = books.get(outcome.token_id)
            if not book or book.ask is None:
                missing = True
                break
            ask_sum += book.ask
            liquidity = min(liquidity, book.ask_size)
            spread_penalty += _spread_penalty(book)
        if missing:
            continue
        edge = 1.0 - ask_sum
        if edge <= config.cost_margin():
            continue
        signals.append(
            Signal(
                signal_type="multi_arb_buy_all",
                market_title=market.title,
                market_id=market.market_id,
                edge=edge,
                score=0.0,
                confidence=_confidence("LOW"),
                liquidity=liquidity if liquidity != float("inf") else 0.0,
                spread_penalty=spread_penalty,
                notes="sum(ask) across outcomes",
                token_ids=[o.token_id for o in market.outcomes],
                event_slug=market.event_slug,
                end_date=market.end_date,
            )
        )
    return signals


def _group_thresholds(
    markets: Iterable[Market],
    books: Dict[str, OrderBookTop],
) -> Dict[Tuple[str, Optional[datetime], str], List[Tuple[float, float, Market, OrderBookTop]]]:
    grouped: Dict[Tuple[str, Optional[datetime], str], List[Tuple[float, float, Market, OrderBookTop]]] = defaultdict(list)
    for market in markets:
        parsed = parse_title(market.title, market.end_date)
        if parsed.pattern != "THRESHOLD" or parsed.strike is None or parsed.underlying is None:
            continue
        if parsed.direction != "above":
            continue
        if not market.outcomes:
            continue
        book = books.get(market.outcomes[0].token_id)
        if not book or book.ask is None:
            continue
        price = book.midpoint if book.midpoint is not None else book.ask
        grouped[(parsed.underlying, parsed.maturity, parsed.direction)].append(
            (parsed.strike, price, market, book)
        )
    return grouped


def detect_monotonicity(
    markets: Iterable[Market],
    books: Dict[str, OrderBookTop],
    config: Config,
) -> List[Signal]:
    signals: List[Signal] = []
    grouped = _group_thresholds(markets, books)
    for key, items in grouped.items():
        items_sorted = sorted(items, key=lambda item: item[0])
        for (strike_low, price_low, market_low, book_low), (
            strike_high,
            price_high,
            market_high,
            book_high,
        ) in zip(items_sorted, items_sorted[1:]):
            delta = price_high - price_low
            if delta <= config.epsilon_monotonicity:
                continue
            liquidity = min(book_low.ask_size, book_high.ask_size)
            spread_penalty = _spread_penalty(book_low) + _spread_penalty(book_high)
            signals.append(
                Signal(
                    signal_type="monotonicity_violation",
                    market_title=f"{market_low.title} vs {market_high.title}",
                    market_id=f"{market_low.market_id}|{market_high.market_id}",
                    edge=delta,
                    score=0.0,
                    confidence=_confidence("MED"),
                    liquidity=liquidity,
                    spread_penalty=spread_penalty,
                    notes=f"strike {strike_low} -> {strike_high} (Δ={delta:.4f})",
                    token_ids=[market_low.outcomes[0].token_id, market_high.outcomes[0].token_id],
                    event_slug=market_low.event_slug,
                    end_date=market_low.end_date,
                    metadata={"underlying": key[0], "maturity": key[1]},
                )
            )
    return signals


def detect_temporal_coherence(
    markets: Iterable[Market],
    books: Dict[str, OrderBookTop],
    config: Config,
) -> List[Signal]:
    signals: List[Signal] = []
    grouped: Dict[str, List[Tuple[datetime, Market, OrderBookTop]]] = defaultdict(list)
    for market in markets:
        if not market.end_date or not market.outcomes:
            continue
        parsed = parse_title(market.title, market.end_date)
        if parsed.pattern == "UNKNOWN":
            continue
        book = books.get(market.outcomes[0].token_id)
        if not book or book.ask is None:
            continue
        grouped[market.title].append((market.end_date, market, book))

    for _, items in grouped.items():
        items_sorted = sorted(items, key=lambda item: item[0])
        for (date_short, market_short, book_short), (
            date_long,
            market_long,
            book_long,
        ) in zip(items_sorted, items_sorted[1:]):
            if book_short.ask is None or book_long.ask is None:
                continue
            if book_short.ask <= book_long.ask + config.epsilon_monotonicity:
                continue
            delta = book_short.ask - book_long.ask
            liquidity = min(book_short.ask_size, book_long.ask_size)
            spread_penalty = _spread_penalty(book_short) + _spread_penalty(book_long)
            signals.append(
                Signal(
                    signal_type="temporal_incoherence",
                    market_title=f"{market_short.title} vs {market_long.title}",
                    market_id=f"{market_short.market_id}|{market_long.market_id}",
                    edge=delta,
                    score=0.0,
                    confidence=_confidence("MED"),
                    liquidity=liquidity,
                    spread_penalty=spread_penalty,
                    notes=f"T1 {date_short.date()} > T2 {date_long.date()}",
                    token_ids=[market_short.outcomes[0].token_id, market_long.outcomes[0].token_id],
                    event_slug=market_short.event_slug,
                    end_date=market_long.end_date,
                )
            )
    return signals
