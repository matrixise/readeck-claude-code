# src/readeck_cli/services/auth.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckAPIError, ReadeckClient


class AuthService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def validate_token(self) -> bool:
        try:
            await self._client.get("/api/profile")
            return True
        except ReadeckAPIError as e:
            if e.status_code == 401:
                return False
            raise
