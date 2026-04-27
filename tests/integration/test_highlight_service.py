# tests/integration/test_highlight_service.py
import httpx
import pytest
import respx
from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.highlights import HighlightService

BASE_URL = "https://readeck.example.com"

HIGHLIGHT_DATA = {
    "id": "h1",
    "bookmark_id": "b1",
    "text": "Important quote",
    "created": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> HighlightService:
    return HighlightService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_highlights_by_bookmark(service: HighlightService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/b1/highlights").mock(
        return_value=httpx.Response(200, json=[HIGHLIGHT_DATA])
    )
    highlights = await service.list(bookmark_id="b1")
    assert len(highlights) == 1
    assert highlights[0].text == "Important quote"


@respx.mock
@pytest.mark.asyncio
async def test_list_all_highlights(service: HighlightService) -> None:
    respx.get(f"{BASE_URL}/api/highlights").mock(
        return_value=httpx.Response(200, json=[HIGHLIGHT_DATA])
    )
    highlights = await service.list()
    assert len(highlights) == 1


@respx.mock
@pytest.mark.asyncio
async def test_delete_highlight(service: HighlightService) -> None:
    respx.delete(f"{BASE_URL}/api/highlights/h1").mock(return_value=httpx.Response(204))
    await service.delete("h1")
