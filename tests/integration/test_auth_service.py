# tests/integration/test_auth_service.py
import httpx
import pytest
import respx

from readeck_cli.client.http import ReadeckClient
from readeck_cli.services.auth import AuthService

BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@pytest.fixture
def service(client: ReadeckClient) -> AuthService:
    return AuthService(client)


@respx.mock
@pytest.mark.asyncio
async def test_validate_token(service: AuthService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(200, json={"username": "stephane"})
    )
    result = await service.validate_token()
    assert result is True


@respx.mock
@pytest.mark.asyncio
async def test_validate_token_returns_false_on_401(service: AuthService) -> None:
    respx.get(f"{BASE_URL}/api/profile").mock(return_value=httpx.Response(401))
    result = await service.validate_token()
    assert result is False
