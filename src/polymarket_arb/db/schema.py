"""SQLAlchemy schema."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from polymarket_arb.db.base import Base


class MarketRow(Base):
    __tablename__ = "markets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    condition_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    liquidity: Mapped[float] = mapped_column(Float, default=0.0)
    token_ids_json: Mapped[str] = mapped_column(Text)


class RawWSEventRow(Base):
    __tablename__ = "raw_ws_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel: Mapped[str] = mapped_column(String(100), index=True)
    market_slug: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OrderbookSnapshotRow(Base):
    __tablename__ = "orderbook_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_slug: Mapped[str] = mapped_column(String(255), index=True)
    token_id: Mapped[str] = mapped_column(String(255), index=True)
    best_bid: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_ask: Mapped[float | None] = mapped_column(Float, nullable=True)
    midpoint: Mapped[float | None] = mapped_column(Float, nullable=True)
    spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    bid_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    ask_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SignalRow(Base):
    __tablename__ = "signals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_type: Mapped[str] = mapped_column(String(100), index=True)
    market_slug: Mapped[str] = mapped_column(String(255), index=True)
    token_id: Mapped[str] = mapped_column(String(255), index=True)
    raw_edge_bps: Mapped[float] = mapped_column(Float)
    net_edge_bps: Mapped[float] = mapped_column(Float)
    details_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PaperOrderRow(Base):
    __tablename__ = "paper_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_slug: Mapped[str] = mapped_column(String(255), index=True)
    token_id: Mapped[str] = mapped_column(String(255), index=True)
    side: Mapped[str] = mapped_column(String(10))
    order_type: Mapped[str] = mapped_column(String(20))
    price: Mapped[float] = mapped_column(Float)
    size: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PaperFillRow(Base):
    __tablename__ = "paper_fills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_order_id: Mapped[int] = mapped_column(Integer, index=True)
    market_slug: Mapped[str] = mapped_column(String(255), index=True)
    token_id: Mapped[str] = mapped_column(String(255), index=True)
    side: Mapped[str] = mapped_column(String(10))
    fill_price: Mapped[float] = mapped_column(Float)
    fill_size: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PositionRow(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_slug: Mapped[str] = mapped_column(String(255), index=True)
    token_id: Mapped[str] = mapped_column(String(255), index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    avg_price: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PnLTimeseriesRow(Base):
    __tablename__ = "pnl_timeseries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    drawdown: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
