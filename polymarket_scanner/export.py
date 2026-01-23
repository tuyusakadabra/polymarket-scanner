from __future__ import annotations

import csv
import json
from dataclasses import asdict
from typing import Iterable

from polymarket_scanner.models import Signal


def export_json(path: str, signals: Iterable[Signal]) -> None:
    payload = [asdict(signal) for signal in signals]
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, default=str)


def export_csv(path: str, signals: Iterable[Signal]) -> None:
    rows = [asdict(signal) for signal in signals]
    if not rows:
        return
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
