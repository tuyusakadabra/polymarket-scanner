"""Edge computation."""


def compute_net_edge_bps(
    raw_edge_bps: float,
    taker_fee_bps: float,
    estimated_slippage_bps: float,
    queue_penalty_bps: float,
    stale_data_penalty_bps: float,
) -> float:
    """Compute net edge after explicit penalties."""
    return (
        raw_edge_bps
        - taker_fee_bps
        - estimated_slippage_bps
        - queue_penalty_bps
        - stale_data_penalty_bps
    )
