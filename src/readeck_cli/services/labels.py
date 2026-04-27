# src/readeck_cli/services/labels.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.label import Label


class LabelService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(self) -> list[Label]:  # ty: ignore[invalid-type-form]
        response = await self._client.get("/api/labels")
        return [Label.model_validate(item) for item in response.json()]

    async def get(self, label_id: str) -> Label:
        response = await self._client.get(f"/api/labels/{label_id}")
        return Label.model_validate(response.json())

    async def create(self, name: str) -> Label:
        response = await self._client.post("/api/labels", json={"label": name})
        return Label.model_validate(response.json())

    async def update(self, label_id: str, name: str) -> Label:
        response = await self._client.patch(
            f"/api/labels/{label_id}", json={"label": name}
        )
        return Label.model_validate(response.json())

    async def delete(self, label_id: str) -> None:
        await self._client.delete(f"/api/labels/{label_id}")
