# src/readeck_cli/services/collections.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.collection import Collection


class CollectionService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self) -> list[Collection]:  # ty: ignore
        response = await self._client.get("/api/collections")
        return [Collection.model_validate(item) for item in response.json()]

    async def get(self, collection_id: str) -> Collection:
        response = await self._client.get(f"/api/collections/{collection_id}")
        return Collection.model_validate(response.json())

    async def create(self, title: str) -> Collection:
        response = await self._client.post("/api/collections", json={"title": title})
        return Collection.model_validate(response.json())

    async def update(self, collection_id: str, title: str) -> Collection:
        response = await self._client.patch(
            f"/api/collections/{collection_id}", json={"title": title}
        )
        return Collection.model_validate(response.json())

    async def delete(self, collection_id: str) -> None:
        await self._client.delete(f"/api/collections/{collection_id}")
