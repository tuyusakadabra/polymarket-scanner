"""CLOB REST helper adapter."""

import httpx


class ClobRestClient:
    """Read-only CLOB REST adapter for top-of-book snapshots.

    Endpoint schemas can vary. This adapter isolates uncertain payload details.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_orderbook(self, token_id: str) -> dict:
        """Fetch orderbook for token id and return raw payload."""
        url = f"{self.base_url}/book"
        params = {"token_id": token_id}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
