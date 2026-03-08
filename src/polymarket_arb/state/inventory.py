"""Paper inventory state."""

from dataclasses import dataclass


@dataclass(slots=True)
class Position:
    """Single token position."""

    quantity: float = 0.0
    avg_price: float = 0.0


class Inventory:
    """Inventory manager for paper mode."""

    def __init__(self) -> None:
        self.positions: dict[tuple[str, str], Position] = {}
        self.realized_pnl: float = 0.0

    def apply_fill(self, market_slug: str, token_id: str, side: str, price: float, size: float) -> Position:
        """Apply fill and update average price / realized PnL."""
        key = (market_slug, token_id)
        pos = self.positions.get(key, Position())
        signed = size if side == "buy" else -size

        if pos.quantity == 0 or pos.quantity * signed > 0:
            new_qty = pos.quantity + signed
            if new_qty != 0:
                pos.avg_price = ((pos.avg_price * pos.quantity) + (price * signed)) / new_qty
            pos.quantity = new_qty
        else:
            close_size = min(abs(pos.quantity), abs(signed))
            if pos.quantity > 0:
                self.realized_pnl += (price - pos.avg_price) * close_size
            else:
                self.realized_pnl += (pos.avg_price - price) * close_size
            pos.quantity += signed
            if pos.quantity == 0:
                pos.avg_price = 0.0

        self.positions[key] = pos
        return pos

    def unrealized_pnl(self, midpoints: dict[tuple[str, str], float]) -> float:
        """Mark-to-mid unrealized pnl."""
        total = 0.0
        for key, pos in self.positions.items():
            midpoint = midpoints.get(key)
            if midpoint is None:
                continue
            total += (midpoint - pos.avg_price) * pos.quantity
        return total

    def total_notional(self, midpoints: dict[tuple[str, str], float]) -> float:
        """Absolute notional exposure."""
        total = 0.0
        for key, pos in self.positions.items():
            midpoint = midpoints.get(key, pos.avg_price)
            total += abs(pos.quantity * midpoint)
        return total
