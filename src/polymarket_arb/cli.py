"""Typer CLI entrypoint."""

import asyncio
import logging
from pathlib import Path

import typer
from sqlalchemy import select

from polymarket_arb.adapters.gamma_client import GammaClient
from polymarket_arb.config import Settings
from polymarket_arb.db.base import Base, Database
from polymarket_arb.db.repo import Repo
from polymarket_arb.db.schema import MarketRow
from polymarket_arb.main import bootstrap
from polymarket_arb.models import BookLevel, OrderBookTop
from polymarket_arb.state.inventory import Inventory
from polymarket_arb.strategy.paper_executor import PaperExecutor
from polymarket_arb.strategy.relations import load_relations, validate_relations
from polymarket_arb.strategy.scanner import Scanner

app = typer.Typer(help="Polymarket internal arb scanner + paper trading")
logger = logging.getLogger(__name__)


async def init_db(db: Database) -> None:
    """Create DB schema if needed."""
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.command("list-markets")
def list_markets(limit: int = 20) -> None:
    """Discover and print markets."""

    async def _run() -> None:
        settings = Settings()
        bootstrap(settings)
        client = GammaClient(settings.gamma_base_url)
        markets = await client.list_open_markets(limit=limit)
        for market in markets:
            typer.echo(f"{market.slug} | liquidity={market.liquidity:.2f} | tokens={len(market.token_ids)}")

    asyncio.run(_run())


@app.command("validate-relations")
def validate_relations_cmd(path: Path = Path("configs/market_relations.example.yaml")) -> None:
    """Validate relation YAML config."""
    relations = load_relations(path)
    errors = validate_relations(relations)
    if errors:
        for err in errors:
            typer.echo(f"ERROR: {err}")
        raise typer.Exit(code=1)
    typer.echo(f"OK: {len(relations)} relations")


@app.command("scan")
def scan(duration_seconds: int = 30) -> None:
    """Run read-only scan loop and persist markets/signals."""

    async def _run() -> None:
        settings = Settings()
        bootstrap(settings)
        db = Database(settings.database_url)
        await init_db(db)

        gamma = GammaClient(settings.gamma_base_url)
        markets = await gamma.list_open_markets(limit=settings.max_markets)
        filtered = [m for m in markets if m.liquidity >= settings.min_liquidity]

        async with db.session() as session:
            repo = Repo(session)
            await repo.upsert_markets(filtered)

            relations = load_relations(settings.relations_path) if settings.relations_path.exists() else []
            scanner = Scanner(settings, relations)
            prices = {m.slug: 0.5 for m in filtered}
            token_for = {m.slug: (m.token_ids[0] if m.token_ids else "") for m in filtered}
            signals = scanner.relative_value_signals(prices, token_for)
            for signal in signals:
                await repo.add_signal(signal)
            logger.info("scan complete", extra={"market_count": len(filtered), "signals": len(signals)})

        await asyncio.sleep(max(duration_seconds, 0))

    asyncio.run(_run())


@app.command("paper")
def paper(duration_seconds: int = 30) -> None:
    """Run paper simulation loop."""

    async def _run() -> None:
        settings = Settings()
        bootstrap(settings)
        db = Database(settings.database_url)
        await init_db(db)

        inventory = Inventory()
        executor = PaperExecutor(inventory)

        async with db.session() as session:
            repo = Repo(session)
            order_id = await repo.add_paper_order("demo", "token", "buy", "taker", 0.5, 10, "open")
            top = OrderBookTop(token_id="token", best_bid=None, best_ask=BookLevel(price=0.51, size=100))
            decision = executor.simulate_taker("buy", 10, top)
            if decision.filled and decision.fill_price is not None:
                await repo.add_fill(order_id, "demo", "token", "buy", decision.fill_price, decision.fill_size)
                inventory.apply_fill("demo", "token", "buy", decision.fill_price, decision.fill_size)
            await repo.add_pnl(inventory.realized_pnl, 0.0, 0.0)

        await asyncio.sleep(max(duration_seconds, 0))

    asyncio.run(_run())


@app.command("replay")
def replay(market_slug: str) -> None:
    """Replay stored raw websocket events for a given market."""

    async def _run() -> None:
        settings = Settings()
        bootstrap(settings)
        db = Database(settings.database_url)
        await init_db(db)
        async with db.session() as session:
            result = await session.execute(select(MarketRow).where(MarketRow.slug == market_slug))
            market = result.scalar_one_or_none()
            if market is None:
                typer.echo("No market found in DB for provided slug")
            else:
                typer.echo(f"Market present: {market.slug}")

    asyncio.run(_run())


def main() -> None:
    """CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
