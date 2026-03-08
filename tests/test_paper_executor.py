from polymarket_arb.models import BookLevel, OrderBookTop
from polymarket_arb.state.inventory import Inventory
from polymarket_arb.strategy.paper_executor import PaperExecutor


def test_taker_fill_and_inventory() -> None:
    inv = Inventory()
    exe = PaperExecutor(inv)
    top = OrderBookTop(
        token_id="t1",
        best_bid=BookLevel(price=0.49, size=100),
        best_ask=BookLevel(price=0.51, size=100),
    )

    decision = exe.simulate_taker(side="buy", size=10, top=top)
    assert decision.filled
    assert decision.fill_price == 0.51

    pos = inv.apply_fill("m1", "t1", "buy", decision.fill_price or 0, 10)
    assert pos.quantity == 10
    assert pos.avg_price == 0.51
