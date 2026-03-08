"""Repository helpers."""

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymarket_arb.models import Market, Signal
from polymarket_arb.db.schema import (
    MarketRow,
    OrderbookSnapshotRow,
    PaperFillRow,
    PaperOrderRow,
    PnLTimeseriesRow,
    PositionRow,
    RawWSEventRow,
    SignalRow,
)


class Repo:
    """Persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_markets(self, markets: list[Market]) -> None:
        for market in markets:
            result = await self.session.execute(select(MarketRow).where(MarketRow.slug == market.slug))
            row = result.scalar_one_or_none()
            if row is None:
                row = MarketRow(
                    slug=market.slug,
                    condition_id=market.condition_id,
                    question=market.question,
                    category=market.category,
                    end_date=market.end_date,
                    liquidity=market.liquidity,
                    token_ids_json=json.dumps(market.token_ids),
                )
                self.session.add(row)
            else:
                row.question = market.question
                row.liquidity = market.liquidity
                row.token_ids_json = json.dumps(market.token_ids)
        await self.session.commit()

    async def add_raw_event(self, channel: str, payload: dict, market_slug: str | None, token_id: str | None) -> None:
        self.session.add(
            RawWSEventRow(
                channel=channel,
                payload_json=json.dumps(payload),
                market_slug=market_slug,
                token_id=token_id,
            )
        )
        await self.session.commit()

    async def add_snapshot(
        self,
        market_slug: str,
        token_id: str,
        best_bid: float | None,
        best_ask: float | None,
        midpoint: float | None,
        spread: float | None,
        bid_size: float | None,
        ask_size: float | None,
    ) -> None:
        self.session.add(
            OrderbookSnapshotRow(
                market_slug=market_slug,
                token_id=token_id,
                best_bid=best_bid,
                best_ask=best_ask,
                midpoint=midpoint,
                spread=spread,
                bid_size=bid_size,
                ask_size=ask_size,
            )
        )
        await self.session.commit()

    async def add_signal(self, signal: Signal) -> None:
        self.session.add(
            SignalRow(
                signal_type=signal.signal_type,
                market_slug=signal.market_slug,
                token_id=signal.token_id,
                raw_edge_bps=signal.raw_edge_bps,
                net_edge_bps=signal.net_edge_bps,
                details_json=json.dumps(signal.details),
            )
        )
        await self.session.commit()

    async def add_paper_order(
        self, market_slug: str, token_id: str, side: str, order_type: str, price: float, size: float, status: str
    ) -> int:
        row = PaperOrderRow(
            market_slug=market_slug,
            token_id=token_id,
            side=side,
            order_type=order_type,
            price=price,
            size=size,
            status=status,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row.id

    async def add_fill(self, paper_order_id: int, market_slug: str, token_id: str, side: str, fill_price: float, fill_size: float) -> None:
        self.session.add(
            PaperFillRow(
                paper_order_id=paper_order_id,
                market_slug=market_slug,
                token_id=token_id,
                side=side,
                fill_price=fill_price,
                fill_size=fill_size,
            )
        )
        await self.session.commit()

    async def upsert_position(self, market_slug: str, token_id: str, quantity: float, avg_price: float) -> None:
        result = await self.session.execute(
            select(PositionRow).where(PositionRow.market_slug == market_slug, PositionRow.token_id == token_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            self.session.add(PositionRow(market_slug=market_slug, token_id=token_id, quantity=quantity, avg_price=avg_price))
        else:
            row.quantity = quantity
            row.avg_price = avg_price
            row.updated_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def add_pnl(self, realized: float, unrealized: float, drawdown: float) -> None:
        self.session.add(PnLTimeseriesRow(realized_pnl=realized, unrealized_pnl=unrealized, drawdown=drawdown))
        await self.session.commit()
