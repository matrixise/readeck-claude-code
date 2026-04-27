# tests/integration/test_profile_service.py
import httpx
import pytest
import respx
from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.profile import ProfileService

BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> ProfileService:
    return ProfileService(client)


@respx.mock
@pytest.mark.asyncio
async def test_get_profile(service: ProfileService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(
            200, json={"username": "stephane", "email": "s@example.com"}
        )
    )
    profile = await service.get()
    assert profile.username == "stephane"
