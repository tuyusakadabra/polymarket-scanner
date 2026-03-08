"""Gamma API client for market discovery."""

from datetime import datetime

import httpx

from polymarket_arb.models import Market


class GammaClient:
    """Read-only market discovery adapter.

    Assumption: the public Gamma API serves market/event collections with fields such as
    `slug`, `question`, `liquidity`, `category`, `endDate`, `tokens`.
    Unknown fields are handled defensively.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def list_open_markets(self, limit: int = 50) -> list[Market]:
        """Fetch open markets and normalize into internal model."""
        url = f"{self.base_url}/markets"
        params = {"active": "true", "closed": "false", "limit": limit}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        markets: list[Market] = []
        for item in data if isinstance(data, list) else data.get("markets", []):
            tokens = item.get("tokens") or []
            token_ids = [str(token.get("token_id") or token.get("id")) for token in tokens if token]
            end_date_raw = item.get("endDate") or item.get("end_date")
            end_date = datetime.fromisoformat(end_date_raw.replace("Z", "+00:00")) if end_date_raw else None
            slug = item.get("slug")
            question = item.get("question")
            if not slug or not question:
                continue
            markets.append(
                Market(
                    slug=str(slug),
                    condition_id=item.get("conditionId") or item.get("condition_id"),
                    question=str(question),
                    category=item.get("category"),
                    end_date=end_date,
                    liquidity=float(item.get("liquidity") or 0.0),
                    token_ids=token_ids,
                )
            )
        return markets
