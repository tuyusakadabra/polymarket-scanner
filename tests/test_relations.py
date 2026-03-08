from polymarket_arb.strategy.relations import Relation, validate_relations


def test_validate_relations_detects_errors() -> None:
    errors = validate_relations(
        [
            Relation("r1", "bad_kind", "a", "b"),
            Relation("r1", "implies", "a", "a"),
        ]
    )
    assert any("duplicate" in error for error in errors)
    assert any("unsupported" in error for error in errors)
    assert any("self" in error for error in errors)
