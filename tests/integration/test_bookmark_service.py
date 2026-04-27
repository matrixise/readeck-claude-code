# tests/integration/test_bookmark_service.py
import httpx
import pytest
import respx
from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.bookmarks import BookmarkService

BASE_URL = "https://readeck.example.com"

BOOKMARK_DATA = {
    "id": "b1",
    "href": "/api/bookmarks/b1",
    "url": "https://example.com",
    "title": "Example",
    "labels": [],
    "is_archived": False,
    "is_marked": False,
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> BookmarkService:
    return BookmarkService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(
            200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"}
        )
    )
    bookmarks, total = await service.list()
    assert len(bookmarks) == 1
    assert total == 1
    assert bookmarks[0].url == "https://example.com"


@respx.mock
@pytest.mark.asyncio
async def test_get_bookmark(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(200, json=BOOKMARK_DATA)
    )
    bm = await service.get("b1")
    assert bm.id == "b1"


@respx.mock
@pytest.mark.asyncio
async def test_create_bookmark(service: BookmarkService) -> None:
    respx.post(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(201, json=BOOKMARK_DATA)
    )
    bm = await service.create("https://example.com")
    assert bm.url == "https://example.com"


@respx.mock
@pytest.mark.asyncio
async def test_update_bookmark(service: BookmarkService) -> None:
    updated = {**BOOKMARK_DATA, "title": "Updated Title"}
    respx.patch(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(200, json=updated)
    )
    bm = await service.update("b1", title="Updated Title")
    assert bm.title == "Updated Title"


@respx.mock
@pytest.mark.asyncio
async def test_delete_bookmark(service: BookmarkService) -> None:
    respx.delete(f"{BASE_URL}/api/bookmarks/b1").mock(return_value=httpx.Response(204))
    await service.delete("b1")


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(
            200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"}
        )
    )
    results = await service.search("example")
    assert len(results) == 1


@respx.mock
@pytest.mark.asyncio
async def test_fetch_all_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(
            200, json=[BOOKMARK_DATA], headers={"X-Total-Count": "1"}
        )
    )
    bookmarks, _ = await service.list(fetch_all=True)
    assert len(bookmarks) == 1
