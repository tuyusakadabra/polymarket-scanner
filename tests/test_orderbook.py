from polymarket_arb.state.orderbook import LocalOrderBook


def test_orderbook_top_and_spread_updates() -> None:
    book = LocalOrderBook(token_id="t1")
    top = book.apply_update(bids=[(0.45, 10), (0.44, 2)], asks=[(0.55, 5), (0.57, 4)])
    assert top.best_bid is not None
    assert top.best_ask is not None
    assert top.best_bid.price == 0.45
    assert top.best_ask.price == 0.55
    assert round(top.spread or 0, 4) == 0.10

    top = book.apply_update(bids=[(0.45, 0)], asks=[])
    assert top.best_bid is not None
    assert top.best_bid.price == 0.44
