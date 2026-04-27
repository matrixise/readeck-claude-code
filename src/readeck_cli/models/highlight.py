from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Highlight(BaseModel):
    id: str
    bookmark_id: str | None = None
    text: str
    created: datetime
    updated: datetime | None = None
