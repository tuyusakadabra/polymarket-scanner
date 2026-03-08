"""Configuration models."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_prefix="POLYMARKET_ARB_", env_file=".env", extra="ignore")

    env: str = "dev"
    log_level: str = "INFO"
    log_json: bool = False

    database_url: str = "sqlite+aiosqlite:///./polymarket_arb.db"

    gamma_base_url: str = "https://gamma-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"

    min_liquidity: float = 0.0
    category: str | None = None
    slug_contains: str | None = None
    max_markets: int = 50

    stale_timeout_seconds: int = 20
    signal_net_edge_bps_threshold: float = 15.0
    taker_fee_bps: float = 10.0
    estimated_slippage_bps: float = 5.0
    queue_penalty_bps: float = 3.0
    stale_data_penalty_bps: float = 10.0
    scan_interval_seconds: float = 5.0
    paper_loop_seconds: float = 2.0

    max_notional_per_market: float = 200.0
    max_total_notional: float = 1000.0
    max_drawdown: float = 150.0

    enable_live_trading: bool = False

    relations_path: Path = Field(default=Path("configs/market_relations.example.yaml"))
