"""Replay raw events from DB."""

import json
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polymarket_arb.db.schema import RawWSEventRow


class ReplayEngine:
    """Iterate persisted websocket events for a market slug."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replay(self, market_slug: str) -> AsyncIterator[dict]:
        """Yield events in insertion order."""
        query = (
            select(RawWSEventRow)
            .where(RawWSEventRow.market_slug == market_slug)
            .order_by(RawWSEventRow.id.asc())
        )
        result = await self.session.execute(query)
        for row in result.scalars():
            yield json.loads(row.payload_json)
