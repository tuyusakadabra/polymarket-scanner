# polymarket_arb_v1

`polymarket_arb_v1` is a production-style Python 3.11 scanner and paper-trading engine for **internal mispricing detection** on Polymarket markets.

This project is intentionally conservative:
- No profitability claims
- No secret/private endpoints
- Read-only mode works without wallet credentials
- Live trading is a disabled stub behind a feature flag

## What it does

- Discovers open markets through documented Polymarket discovery APIs (Gamma)
- Ingests real-time-like order book updates (via documented patterns / adapters)
- Maintains local top-of-book state
- Computes edge with explicit penalties
- Emits paper signals only when net edge threshold is exceeded
- Simulates maker/taker paper fills with risk limits and kill switches
- Persists events, snapshots, signals, orders, fills, positions, and PnL in SQL

## Architecture

```text
            +------------------------------+
            |         Typer CLI            |
            | scan | paper | replay | ...  |
            +---------------+--------------+
                            |
                            v
       +---------------------------------------------+
       |                 App Core                    |
       | Scanner | PaperExecutor | ReplayEngine      |
       +------------------+--------------------------+
                          |
      +-------------------+--------------------+
      |                                        |
      v                                        v
+-------------+                        +---------------+
| Adapters    |                        | Strategy      |
| Gamma REST  |                        | Relations     |
| CLOB REST   |                        | Fair Value    |
| Market WS   |                        | Edge Model    |
+------+------+                        +-------+-------+
       |                                        |
       +--------------------+-------------------+
                            v
                 +----------------------+
                 | Local State + DB     |
                 | OrderBookState       |
                 | SQLAlchemy repos     |
                 +----------------------+
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

## Configuration

1. Copy `.env.example` to `.env` and adjust values.
2. Optional: provide `configs/market_relations.yaml` based on the example file.

## Read-only mode usage

List markets:

```bash
python -m polymarket_arb.cli list-markets --limit 20
```

Run scanner:

```bash
python -m polymarket_arb.cli scan --duration-seconds 60
```

## Paper trading usage

```bash
python -m polymarket_arb.cli paper --duration-seconds 120
```

## Replay usage

```bash
python -m polymarket_arb.cli replay --market-slug us-election-winner-democrat
```

## Validate relations

```bash
python -m polymarket_arb.cli validate-relations --path configs/market_relations.example.yaml
```

## Limitations

- Public APIs may evolve; adapters isolate uncertain payload fields.
- WebSocket schemas vary by channel, so parsing is resilient and stores raw events for replay.
- V1 focuses on top-of-book and paper fills, not deep queue position certainty.

## Safe path to live execution later

1. Keep scanner/paper pipeline unchanged.
2. Add authenticated order-routing adapter with explicit interface contract.
3. Gate with `enable_live_trading=true` + additional risk approvals.
4. Run shadow mode comparing paper vs live acknowledgements before enabling capital.
