"""Relation parsing and validation."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class Relation:
    """Generic relation config."""

    relation_id: str
    kind: str
    left_market_slug: str
    right_market_slug: str
    threshold_bps: float = 0.0
    max_positive_bps: float = 0.0
    max_negative_bps: float = 0.0


def load_relations(path: Path) -> list[Relation]:
    """Load relations YAML."""
    payload = yaml.safe_load(path.read_text())
    rows = payload.get("relations", []) if isinstance(payload, dict) else []
    return [Relation(**row) for row in rows]


def validate_relations(relations: list[Relation]) -> list[str]:
    """Return validation errors."""
    errors: list[str] = []
    seen: set[str] = set()
    for relation in relations:
        if relation.relation_id in seen:
            errors.append(f"duplicate relation_id={relation.relation_id}")
        seen.add(relation.relation_id)
        if relation.kind not in {"implies", "bounded_spread"}:
            errors.append(f"unsupported kind={relation.kind}")
        if relation.left_market_slug == relation.right_market_slug:
            errors.append(f"self relation_id={relation.relation_id}")
    return errors
