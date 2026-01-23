from __future__ import annotations

import logging
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from polymarket_scanner.clob_client import ClobClient
from polymarket_scanner.config import Config, ScanOptions
from polymarket_scanner.export import export_csv, export_json
from polymarket_scanner.gamma_client import GammaClient
from polymarket_scanner.models import Market, OrderBookTop, Signal
from polymarket_scanner.ranker import rank_signals
from polymarket_scanner.signals_noarb import (
    detect_binary_complement,
    detect_monotonicity,
    detect_multi_noarb,
    detect_temporal_coherence,
)
from polymarket_scanner.utils import TTLCache

app = typer.Typer(add_completion=False)
console = Console()


def _setup_logging(level: str) -> None:
    logging.basicConfig(level=level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _fetch_orderbooks(markets: List[Market], clob: ClobClient) -> Dict[str, OrderBookTop]:
    books: Dict[str, OrderBookTop] = {}
    for market in markets:
        for outcome in market.outcomes:
            if outcome.token_id in books:
                continue
            book = clob.fetch_orderbook_top(outcome.token_id)
            if book:
                books[outcome.token_id] = book
    return books


def _render_table(signals: List[Signal]) -> None:
    table = Table(title="Polymarket Scanner Signals")
    table.add_column("Score", justify="right")
    table.add_column("Type")
    table.add_column("Market")
    table.add_column("Expiry")
    table.add_column("Edge", justify="right")
    table.add_column("Liquidity", justify="right")
    table.add_column("Confidence")
    table.add_column("Notes")

    for signal in signals:
        table.add_row(
            f"{signal.score:.4f}",
            signal.signal_type,
            signal.market_title,
            signal.end_date.strftime("%Y-%m-%d") if signal.end_date else "-",
            f"{signal.edge:.4f}",
            f"{signal.liquidity:.2f}",
            signal.confidence,
            signal.notes,
        )
    console.print(table)


@app.command()
def scan(
    query: Optional[str] = typer.Option(None, "--query", help="Query string for markets"),
    top: int = typer.Option(30, "--top", help="Top N signals to display"),
    min_liquidity: float = typer.Option(50.0, "--min-liquidity", help="Minimum executable liquidity"),
    min_volume: float = typer.Option(0.0, "--min-volume", help="Minimum 24h volume"),
    export_json_path: Optional[str] = typer.Option(None, "--export", help="Export JSON file path"),
    export_csv_path: Optional[str] = typer.Option(None, "--export-csv", help="Export CSV file path"),
    event_slug: Optional[str] = typer.Option(None, "--event-slug", help="Filter by event slug"),
    gamma_base_url: str = typer.Option("https://gamma-api.polymarket.com", "--gamma-base-url"),
    clob_base_url: str = typer.Option("https://clob.polymarket.com", "--clob-base-url"),
    safety_margin: float = typer.Option(0.005, "--safety-margin"),
    epsilon_monotonicity: float = typer.Option(0.01, "--epsilon-monotonicity"),
    cache_ttl: int = typer.Option(15, "--cache-ttl"),
    fee_rate_bps: float = typer.Option(0.0, "--fee-rate-bps"),
    log_level: str = typer.Option("INFO", "--log-level"),
) -> None:
    config = Config(
        gamma_base_url=gamma_base_url,
        clob_base_url=clob_base_url,
        safety_margin=safety_margin,
        epsilon_monotonicity=epsilon_monotonicity,
        cache_ttl_seconds=cache_ttl,
        fee_rate_bps=fee_rate_bps,
        min_liquidity=min_liquidity,
        min_volume=min_volume,
        log_level=log_level,
    )
    _setup_logging(config.log_level)
    cache = TTLCache(config.cache_ttl_seconds)
    gamma = GammaClient(config, cache)
    clob = ClobClient(config, cache)

    options = ScanOptions(
        query=query,
        top=top,
        min_liquidity=min_liquidity,
        min_volume=min_volume,
        export_json=export_json_path,
        export_csv=export_csv_path,
        event_slug=event_slug,
    )

    markets = gamma.fetch_markets(options.query, limit=500, min_volume=options.min_volume, event_slug=options.event_slug)
    if not markets:
        console.print("[yellow]No markets found.[/yellow]")
        raise typer.Exit(code=0)

    books = _fetch_orderbooks(markets, clob)

    signals: List[Signal] = []
    signals.extend(detect_binary_complement(markets, books, config))
    signals.extend(detect_multi_noarb(markets, books, config))
    signals.extend(detect_monotonicity(markets, books, config))
    signals.extend(detect_temporal_coherence(markets, books, config))

    signals = [s for s in signals if s.liquidity >= options.min_liquidity]
    ranked = rank_signals(signals)[: options.top]
    _render_table(ranked)

    if options.export_json:
        export_json(options.export_json, ranked)
    if options.export_csv:
        export_csv(options.export_csv, ranked)
