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
    "loaded": True,
    "labels": [],
    "is_archived": False,
    "is_marked": False,
    "is_deleted": False,
    "read_progress": 0,
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-01-01T00:00:00Z",
}

BOOKMARK_UPDATED_DATA = {
    "id": "b1",
    "href": "/api/bookmarks/b1",
    "title": "Updated Title",
    "updated": "2026-01-02T00:00:00Z",
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
            200, json=[BOOKMARK_DATA], headers={"Total-Count": "1"}
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
        return_value=httpx.Response(
            202,
            json={"status": 202, "message": "Link submited"},
            headers={"Bookmark-ID": "b1"},
        )
    )
    bookmark_id = await service.create("https://example.com")
    assert bookmark_id == "b1"


@respx.mock
@pytest.mark.asyncio
async def test_update_bookmark(service: BookmarkService) -> None:
    respx.patch(f"{BASE_URL}/api/bookmarks/b1").mock(
        return_value=httpx.Response(200, json=BOOKMARK_UPDATED_DATA)
    )
    bm = await service.update("b1", title="Updated Title")
    assert bm.title == "Updated Title"
    assert bm.id == "b1"


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
            200, json=[BOOKMARK_DATA], headers={"Total-Count": "1"}
        )
    )
    results = await service.search(search="example")
    assert len(results) == 1


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks_by_title(service: BookmarkService) -> None:
    route = respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA])
    )
    results = await service.search(title="Example")
    assert len(results) == 1
    assert "title=Example" in str(route.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks_date_range(service: BookmarkService) -> None:
    route = respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA])
    )
    results = await service.search(range_start="2026-01-01", range_end="2026-12-31")
    assert len(results) == 1
    url_str = str(route.calls[0].request.url)
    assert "range_start=2026-01-01" in url_str
    assert "range_end=2026-12-31" in url_str


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks_is_archived(service: BookmarkService) -> None:
    route = respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA])
    )
    results = await service.search(is_archived=True)
    assert len(results) == 1
    assert "is_archived=true" in str(route.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks_read_status(service: BookmarkService) -> None:
    route = respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA])
    )
    results = await service.search(read_status=["unread", "reading"])
    assert len(results) == 1
    url_str = str(route.calls[0].request.url)
    assert "read_status=unread" in url_str
    assert "read_status=reading" in url_str


@respx.mock
@pytest.mark.asyncio
async def test_search_bookmarks_collection(service: BookmarkService) -> None:
    route = respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[BOOKMARK_DATA])
    )
    results = await service.search(collection="col1")
    assert len(results) == 1
    assert "collection=col1" in str(route.calls[0].request.url)


@respx.mock
@pytest.mark.asyncio
async def test_fetch_all_bookmarks(service: BookmarkService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(
            200, json=[BOOKMARK_DATA], headers={"Total-Count": "1"}
        )
    )
    bookmarks, _ = await service.list(fetch_all=True)
    assert len(bookmarks) == 1
