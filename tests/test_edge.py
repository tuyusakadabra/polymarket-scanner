from polymarket_arb.strategy.edge import compute_net_edge_bps


def test_edge_computation() -> None:
    net = compute_net_edge_bps(
        raw_edge_bps=50,
        taker_fee_bps=10,
        estimated_slippage_bps=5,
        queue_penalty_bps=3,
        stale_data_penalty_bps=7,
    )
    assert net == 25
