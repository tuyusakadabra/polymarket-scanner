"""In-memory market cache."""

from polymarket_arb.models import Market


class MarketCache:
    """Caches discovered markets and token->slug mapping."""

    def __init__(self) -> None:
        self.by_slug: dict[str, Market] = {}
        self.token_to_slug: dict[str, str] = {}

    def load(self, markets: list[Market]) -> None:
        for market in markets:
            self.by_slug[market.slug] = market
            for token_id in market.token_ids:
                self.token_to_slug[token_id] = market.slug

    def selected_markets(
        self,
        min_liquidity: float,
        category: str | None,
        slug_contains: str | None,
        limit: int,
    ) -> list[Market]:
        result = []
        for market in self.by_slug.values():
            if market.liquidity < min_liquidity:
                continue
            if category and (market.category or "").lower() != category.lower():
                continue
            if slug_contains and slug_contains.lower() not in market.slug.lower():
                continue
            result.append(market)
        return result[:limit]
