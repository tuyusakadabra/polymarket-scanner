"""Market websocket adapter."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator

import websockets

logger = logging.getLogger(__name__)


class MarketWSClient:
    """WebSocket client with reconnect and exponential backoff."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def stream(self, token_ids: list[str]) -> AsyncIterator[dict]:
        """Yield market events from websocket channel."""
        backoff = 1.0
        while True:
            ws_url = self.base_url.replace("http", "ws") + "/ws/market"
            try:
                async with websockets.connect(ws_url, ping_interval=20) as ws:
                    subscribe = {"type": "subscribe", "channel": "market", "token_ids": token_ids}
                    await ws.send(json.dumps(subscribe))
                    logger.info("market ws subscribed", extra={"token_count": len(token_ids)})
                    backoff = 1.0
                    while True:
                        msg = await ws.recv()
                        yield json.loads(msg)
            except Exception as exc:
                logger.warning("market ws reconnecting", extra={"error": str(exc), "backoff": backoff})
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
