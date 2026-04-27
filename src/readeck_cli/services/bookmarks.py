from __future__ import annotations

from collections.abc import Sequence
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

    async def search(
        self,
        search: str | None = None,
        title: str | None = None,
        author: str | None = None,
        site: str | None = None,
        type: Sequence[str] | None = None,
        labels: str | None = None,
        is_loaded: bool | None = None,
        has_errors: bool | None = None,
        has_labels: bool | None = None,
        is_archived: bool | None = None,
        is_marked: bool | None = None,
        range_start: str | None = None,
        range_end: str | None = None,
        read_status: Sequence[str] | None = None,
        id: str | None = None,
        collection: str | None = None,
        sort: Sequence[str] | None = None,
        limit: int = 100,
    ) -> list[Bookmark]:  # type: ignore[valid-type]  # ty: ignore
        params: dict[str, Any] = {"limit": limit}
        if search is not None:
            params["search"] = search
        if title is not None:
            params["title"] = title
        if author is not None:
            params["author"] = author
        if site is not None:
            params["site"] = site
        if type is not None:
            params["type"] = type
        if labels is not None:
            params["labels"] = labels
        if is_loaded is not None:
            params["is_loaded"] = str(is_loaded).lower()
        if has_errors is not None:
            params["has_errors"] = str(has_errors).lower()
        if has_labels is not None:
            params["has_labels"] = str(has_labels).lower()
        if is_archived is not None:
            params["is_archived"] = str(is_archived).lower()
        if is_marked is not None:
            params["is_marked"] = str(is_marked).lower()
        if range_start is not None:
            params["range_start"] = range_start
        if range_end is not None:
            params["range_end"] = range_end
        if read_status is not None:
            params["read_status"] = read_status
        if id is not None:
            params["id"] = id
        if collection is not None:
            params["collection"] = collection
        if sort is not None:
            params["sort"] = sort
        response = await self._client.get("/api/bookmarks", params=params)
        return [Bookmark.model_validate(item) for item in response.json()]

    async def export(self, bookmark_id: str, fmt: str = "md") -> bytes:
        return await self._client.get_bytes(
            f"/api/bookmarks/{bookmark_id}/article.{fmt}"
        )
