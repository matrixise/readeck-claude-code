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
    respx.get(f"{BASE_URL}/api/labels").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": "l1", "label": "python", "count": 5},
                {"id": "l2", "label": "go", "count": 2},
            ],
        )
    )
    labels = await service.list()
    assert len(labels) == 2
    assert labels[0].label == "python"


@respx.mock
@pytest.mark.asyncio
async def test_get_label(service: LabelService) -> None:
    respx.get(f"{BASE_URL}/api/labels/l1").mock(
        return_value=httpx.Response(
            200, json={"id": "l1", "label": "python", "count": 5}
        )
    )
    label = await service.get("l1")
    assert label.id == "l1"


@respx.mock
@pytest.mark.asyncio
async def test_create_label(service: LabelService) -> None:
    respx.post(f"{BASE_URL}/api/labels").mock(
        return_value=httpx.Response(201, json={"id": "l3", "label": "rust", "count": 0})
    )
    label = await service.create("rust")
    assert label.label == "rust"


@respx.mock
@pytest.mark.asyncio
async def test_update_label(service: LabelService) -> None:
    respx.patch(f"{BASE_URL}/api/labels/l1").mock(
        return_value=httpx.Response(
            200, json={"id": "l1", "label": "python3", "count": 5}
        )
    )
    label = await service.update("l1", name="python3")
    assert label.label == "python3"


@respx.mock
@pytest.mark.asyncio
async def test_delete_label(service: LabelService) -> None:
    respx.delete(f"{BASE_URL}/api/labels/l1").mock(return_value=httpx.Response(204))
    await service.delete("l1")
