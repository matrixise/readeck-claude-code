from __future__ import annotations

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: str | None = None
    username: str
    email: str | None = None
