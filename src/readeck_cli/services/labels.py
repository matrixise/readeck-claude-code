# src/readeck_cli/services/labels.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient
from readeck_cli.models.label import Label


class LabelService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self) -> list[Label]:  # ty: ignore
        response = await self._client.get("/api/bookmarks/labels")
        return [Label.model_validate(item) for item in response.json()]

    async def get(self, name: str) -> Label:
        response = await self._client.get(
            "/api/bookmarks/labels", params={"name": name}
        )
        items = response.json()
        if not items:
            raise ReadeckAPIError(404, "Label not found.")
        return Label.model_validate(items[0])

    async def create(self, name: str) -> Label:
        response = await self._client.post(
            "/api/bookmarks/labels", json={"label": name}
        )
        return Label.model_validate(response.json())

    async def update(self, name: str, new_name: str) -> Label:
        response = await self._client.patch(
            "/api/bookmarks/labels", params={"name": name}, json={"label": new_name}
        )
        return Label.model_validate(response.json())

    async def delete(self, name: str) -> None:
        await self._client.delete("/api/bookmarks/labels", params={"name": name})
