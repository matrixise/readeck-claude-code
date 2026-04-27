# src/readeck_cli/services/highlights.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.highlight import Highlight


class HighlightService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self, bookmark_id: str | None = None) -> list[Highlight]:  # ty: ignore
        if bookmark_id:
            path = f"/api/bookmarks/{bookmark_id}/highlights"
        else:
            path = "/api/highlights"
        response = await self._client.get(path)
        return [Highlight.model_validate(item) for item in response.json()]

    async def delete(self, highlight_id: str) -> None:
        await self._client.delete(f"/api/highlights/{highlight_id}")
