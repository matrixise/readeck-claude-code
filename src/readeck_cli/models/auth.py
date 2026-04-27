from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TokenInfo(BaseModel):
    id: str
    token: str
    application: str
    created: datetime
    expires: datetime | None = None
