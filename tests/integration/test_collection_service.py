# tests/integration/test_collection_service.py
import httpx
import pytest
import respx
from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.collections import CollectionService

BASE_URL = "https://readeck.example.com"

COLLECTION_DATA = {
    "id": "c1",
    "title": "Reading List",
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-01-01T00:00:00Z",
}


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> CollectionService:
    return CollectionService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_collections(service: CollectionService) -> None:
    respx.get(f"{BASE_URL}/api/collections").mock(
        return_value=httpx.Response(200, json=[COLLECTION_DATA])
    )
    collections = await service.list()
    assert len(collections) == 1
    assert collections[0].title == "Reading List"


@respx.mock
@pytest.mark.asyncio
async def test_get_collection(service: CollectionService) -> None:
    respx.get(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(200, json=COLLECTION_DATA)
    )
    col = await service.get("c1")
    assert col.id == "c1"


@respx.mock
@pytest.mark.asyncio
async def test_create_collection(service: CollectionService) -> None:
    respx.post(f"{BASE_URL}/api/collections").mock(
        return_value=httpx.Response(201, json=COLLECTION_DATA)
    )
    col = await service.create("Reading List")
    assert col.title == "Reading List"


@respx.mock
@pytest.mark.asyncio
async def test_update_collection(service: CollectionService) -> None:
    updated = {**COLLECTION_DATA, "title": "Archive"}
    respx.patch(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(200, json=updated)
    )
    col = await service.update("c1", title="Archive")
    assert col.title == "Archive"


@respx.mock
@pytest.mark.asyncio
async def test_delete_collection(service: CollectionService) -> None:
    respx.delete(f"{BASE_URL}/api/collections/c1").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("c1")
