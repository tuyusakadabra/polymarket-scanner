# Polymarket Scanner

Outil CLI Python pour scanner les marchés Polymarket via l’API Gamma + l’API CLOB et détecter des incohérences de prix (sans exécuter de trades).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python -m polymarket_scanner scan --query "Bitcoin" --top 30 --min-liquidity 50
```

Exemples avancés :

```bash
python -m polymarket_scanner scan \
  --query "Bitcoin" \
  --min-volume 10000 \
  --export out.json \
  --export-csv out.csv \
  --log-level DEBUG
```

## Signaux (MVP 1)

- **Binary YES/NO complement** : si `ask_yes + ask_no < 1 - cost_margin`.
- **Multi-issues (LOW confidence)** : somme des asks < 1 pour des issues mutuellement exclusives.
- **Monotonicité threshold** : `P(>K1) >= P(>K2)` pour `K1 < K2`.
- **Cohérence temporelle** : probabilité d’un même événement ne doit pas baisser avec une maturité plus longue.

## Architecture

```
polymarket_scanner/
  config.py
  gamma_client.py
  clob_client.py
  models.py
  parsing.py
  signals_noarb.py
  ranker.py
  cli.py
  export.py
  utils.py
```

## Tests

```bash
pytest
```

## Notes

- Aucun trade n’est exécuté.
- Le code utilise un cache TTL et une stratégie de retry simple.
- Les endpoints sont configurables via options CLI.
