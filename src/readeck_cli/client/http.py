# src/readeck_cli/client/http.py
from __future__ import annotations

from typing import Any

import httpx


class ReadeckAPIError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class ReadeckClient:
    def __init__(self, url: str, token: str) -> None:
        self._base_url = url.rstrip("/")
        self._token = token
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        response = await self._client.get(path, params=params)
        self._raise_for_status(response)
        return response

    async def post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        response = await self._client.post(path, json=json)
        self._raise_for_status(response)
        return response

    async def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        response = await self._client.patch(path, json=json, params=params)
        self._raise_for_status(response)
        return response

    async def delete(
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        response = await self._client.delete(path, params=params)
        self._raise_for_status(response)
        return response

    async def get_bytes(self, path: str) -> bytes:
        response = await self._client.get(path)
        self._raise_for_status(response)
        return response.content

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> ReadeckClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    @classmethod
    async def create_token(
        cls, url: str, username: str, password: str, application: str = "readeck-cli"
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=url.rstrip("/"), timeout=30.0) as client:
            response = await client.post(
                "/api/auth",
                json={
                    "application": application,
                    "username": username,
                    "password": password,
                },
            )
            if response.status_code == 401:
                raise ReadeckAPIError(401, "Invalid username or password.")
            if response.status_code >= 400:
                raise ReadeckAPIError(response.status_code, response.text)
            return dict(response.json())

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise ReadeckAPIError(
                401, "Invalid or expired token. Run 'readeck-cli auth login'."
            )
        if response.status_code == 403:
            raise ReadeckAPIError(403, "Forbidden.")
        if response.status_code == 404:
            raise ReadeckAPIError(404, "Resource not found.")
        if response.status_code == 422:
            raise ReadeckAPIError(422, f"Validation error: {response.text}")
        if response.status_code >= 500:
            raise ReadeckAPIError(
                response.status_code, f"Server error: {response.text}"
            )
