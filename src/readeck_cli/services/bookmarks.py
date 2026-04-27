from __future__ import annotations

from typing import Any

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.bookmark import Bookmark, BookmarkUpdated


class BookmarkService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        fetch_all: bool = False,
    ) -> tuple[list[Bookmark], int]:  # ty: ignore
        if fetch_all:
            items = await self._fetch_all()
            return items, len(items)
        params: dict[str, int] = {"offset": (page - 1) * limit, "limit": limit}
        response = await self._client.get("/api/bookmarks", params=params)
        total = int(response.headers.get("total-count", 0))
        return [Bookmark.model_validate(item) for item in response.json()], total

    async def _fetch_all(self) -> list[Bookmark]:  # type: ignore[valid-type]  # ty: ignore
        all_items: list[Bookmark] = []
        offset = 0
        limit = 100
        while True:
            params: dict[str, int] = {"offset": offset, "limit": limit}
            response = await self._client.get("/api/bookmarks", params=params)
            total = int(response.headers.get("total-count", 0))
            items = response.json()
            if not items:
                break
            all_items.extend(Bookmark.model_validate(item) for item in items)
            if len(all_items) >= total:
                break
            offset += limit
        return all_items

    async def get(self, bookmark_id: str) -> Bookmark:
        response = await self._client.get(f"/api/bookmarks/{bookmark_id}")
        return Bookmark.model_validate(response.json())

    async def create(self, url: str) -> str:
        response = await self._client.post("/api/bookmarks", json={"url": url})
        return str(response.headers.get("bookmark-id", ""))

    async def update(self, bookmark_id: str, **kwargs: Any) -> BookmarkUpdated:
        response = await self._client.patch(
            f"/api/bookmarks/{bookmark_id}", json=kwargs
        )
        return BookmarkUpdated.model_validate(response.json())

    async def delete(self, bookmark_id: str) -> None:
        await self._client.delete(f"/api/bookmarks/{bookmark_id}")

    async def search(self, query: str) -> list[Bookmark]:  # type: ignore[valid-type]  # ty: ignore
        params: dict[str, str | int] = {"search": query, "limit": 100}
        response = await self._client.get("/api/bookmarks", params=params)
        return [Bookmark.model_validate(item) for item in response.json()]

    async def export(self, bookmark_id: str, fmt: str = "epub") -> bytes:
        return await self._client.get_bytes(
            f"/api/bookmarks/{bookmark_id}/article.{fmt}"
        )
