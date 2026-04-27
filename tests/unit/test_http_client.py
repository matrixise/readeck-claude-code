# tests/unit/test_http_client.py
import httpx
import pytest
import respx
from readeck_cli.client.http import ReadeckAPIError, ReadeckClient

BASE_URL = "https://readeck.example.com"


@pytest.fixture
def client() -> ReadeckClient:
    return ReadeckClient(url=BASE_URL, token="testtoken")


@respx.mock
@pytest.mark.asyncio
async def test_get_success(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(200, json=[{"id": "1"}])
    )
    response = await client.get("/api/bookmarks")
    assert response.status_code == 200
    assert response.json() == [{"id": "1"}]


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_401(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks").mock(return_value=httpx.Response(401))
    with pytest.raises(ReadeckAPIError) as exc_info:
        await client.get("/api/bookmarks")
    assert exc_info.value.status_code == 401
    assert "token" in str(exc_info.value).lower()


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_404(client: ReadeckClient) -> None:
    respx.get(f"{BASE_URL}/api/bookmarks/missing").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(ReadeckAPIError) as exc_info:
        await client.get("/api/bookmarks/missing")
    assert exc_info.value.status_code == 404


@respx.mock
@pytest.mark.asyncio
async def test_bearer_token_injected(client: ReadeckClient) -> None:
    route = respx.get(f"{BASE_URL}/api/profile").mock(
        return_value=httpx.Response(200, json={})
    )
    await client.get("/api/profile")
    assert route.calls[0].request.headers["authorization"] == "Bearer testtoken"


@respx.mock
@pytest.mark.asyncio
async def test_post_success(client: ReadeckClient) -> None:
    respx.post(f"{BASE_URL}/api/bookmarks").mock(
        return_value=httpx.Response(201, json={"id": "new"})
    )
    response = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    assert response.json()["id"] == "new"


@respx.mock
@pytest.mark.asyncio
async def test_delete_success(client: ReadeckClient) -> None:
    respx.delete(f"{BASE_URL}/api/bookmarks/1").mock(return_value=httpx.Response(204))
    response = await client.delete("/api/bookmarks/1")
    assert response.status_code == 204


@respx.mock
@pytest.mark.asyncio
async def test_create_token_classmethod() -> None:
    respx.post(f"{BASE_URL}/api/auth").mock(
        return_value=httpx.Response(200, json={"id": "tid", "token": "newtoken"})
    )
    result = await ReadeckClient.create_token(BASE_URL, "user", "pass")
    assert result["token"] == "newtoken"
