"""Scanner logic."""

from dataclasses import dataclass
from datetime import datetime, timezone

from polymarket_arb.config import Settings
from polymarket_arb.models import Signal
from polymarket_arb.state.orderbook import LocalOrderBook
from polymarket_arb.strategy.edge import compute_net_edge_bps
from polymarket_arb.strategy.relations import Relation


@dataclass(slots=True)
class ScannerResult:
    """Bundle of generated signals."""

    signals: list[Signal]


class Scanner:
    """Generates sanity + relative-value signals."""

    def __init__(self, settings: Settings, relations: list[Relation]) -> None:
        self.settings = settings
        self.relations = relations

    def sanity_signal(self, market_slug: str, token_id: str, book: LocalOrderBook) -> Signal | None:
        """Emit sanity warning when book appears stale or crossed."""
        top = book.top()
        age = (datetime.now(timezone.utc) - top.updated_at).total_seconds()
        if age > self.settings.stale_timeout_seconds:
            return Signal(
                signal_type="sanity_stale",
                market_slug=market_slug,
                token_id=token_id,
                raw_edge_bps=0.0,
                net_edge_bps=-999,
                details={"age_seconds": age},
            )
        if top.spread is not None and top.spread < 0:
            return Signal(
                signal_type="sanity_crossed",
                market_slug=market_slug,
                token_id=token_id,
                raw_edge_bps=0.0,
                net_edge_bps=-999,
                details={"spread": top.spread},
            )
        return None

    def relative_value_signals(self, prices_by_slug: dict[str, float], token_for_slug: dict[str, str]) -> list[Signal]:
        """Evaluate configured relation constraints."""
        out: list[Signal] = []
        for rel in self.relations:
            left = prices_by_slug.get(rel.left_market_slug)
            right = prices_by_slug.get(rel.right_market_slug)
            if left is None or right is None:
                continue
            raw_bps = (left - right) * 10_000
            if rel.kind == "implies" and raw_bps <= rel.threshold_bps:
                continue
            if rel.kind == "bounded_spread" and (-rel.max_negative_bps <= raw_bps <= rel.max_positive_bps):
                continue

            net = compute_net_edge_bps(
                raw_bps,
                self.settings.taker_fee_bps,
                self.settings.estimated_slippage_bps,
                self.settings.queue_penalty_bps,
                self.settings.stale_data_penalty_bps,
            )
            if net < self.settings.signal_net_edge_bps_threshold:
                continue
            out.append(
                Signal(
                    signal_type=f"rv_{rel.kind}",
                    market_slug=rel.left_market_slug,
                    token_id=token_for_slug.get(rel.left_market_slug, ""),
                    raw_edge_bps=raw_bps,
                    net_edge_bps=net,
                    details={"relation_id": rel.relation_id, "left": left, "right": right},
                )
            )
        return out
