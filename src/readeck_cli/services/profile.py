# src/readeck_cli/services/profile.py
from __future__ import annotations

from readeck_cli.client.http import ReadeckClient
from readeck_cli.models.profile import UserProfile


class ProfileService:
    def __init__(self, client: ReadeckClient) -> None:
        self._client = client

    async def get(self) -> UserProfile:
        response = await self._client.get("/api/profile")
        return UserProfile.model_validate(response.json())
