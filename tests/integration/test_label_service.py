# tests/integration/test_label_service.py
import httpx
import pytest
import respx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.labels import LabelService

BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> LabelService:
    return LabelService(client)


@respx.mock
@pytest.mark.asyncio
async def test_list_labels(service: LabelService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/labels").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "python",
                    "count": 5,
                    "href": "/api/bookmarks/labels?name=python",
                    "href_bookmarks": "/api/bookmarks?labels=%22python%22",
                },
                {
                    "name": "go",
                    "count": 2,
                    "href": "/api/bookmarks/labels?name=go",
                    "href_bookmarks": "/api/bookmarks?labels=%22go%22",
                },
            ],
        )
    )
    labels = await service.list()
    assert len(labels) == 2
    assert labels[0].name == "python"


@respx.mock
@pytest.mark.asyncio
async def test_get_label(service: LabelService) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/labels").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "python",
                    "count": 5,
                    "href": "/api/bookmarks/labels?name=python",
                    "href_bookmarks": "/api/bookmarks?labels=%22python%22",
                }
            ],
        )
    )
    label = await service.get("python")
    assert label.name == "python"


@respx.mock
@pytest.mark.asyncio
async def test_create_label(service: LabelService) -> None:
    respx.post(f"{BASE_URL}/api/bookmarks/labels").mock(
        return_value=httpx.Response(
            201,
            json={
                "name": "rust",
                "count": 0,
                "href": "/api/bookmarks/labels?name=rust",
                "href_bookmarks": "/api/bookmarks?labels=%22rust%22",
            },
        )
    )
    label = await service.create("rust")
    assert label.name == "rust"


@respx.mock
@pytest.mark.asyncio
async def test_update_label(service: LabelService) -> None:
    respx.patch(f"{BASE_URL}/api/bookmarks/labels").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "python3",
                "count": 5,
                "href": "/api/bookmarks/labels?name=python3",
                "href_bookmarks": "/api/bookmarks?labels=%22python3%22",
            },
        )
    )
    label = await service.update("python", new_name="python3")
    assert label.name == "python3"


@respx.mock
@pytest.mark.asyncio
async def test_delete_label(service: LabelService) -> None:
    respx.delete(f"{BASE_URL}/api/bookmarks/labels").mock(
        return_value=httpx.Response(204)
    )
    await service.delete("python")
