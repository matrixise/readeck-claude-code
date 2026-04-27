from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Collection(BaseModel):
    id: str
    title: str
    created: datetime
    updated: datetime
