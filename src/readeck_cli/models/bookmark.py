from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BookmarkImage(BaseModel):
    src: str
    width: int | None = None
    height: int | None = None


class Bookmark(BaseModel):
    id: str
    href: str
    url: str
    title: str
    type: str | None = None
    description: str | None = None
    authors: list[str] = []
    lang: str | None = None
    labels: list[str] = []
    is_archived: bool = False
    is_marked: bool = False
    reading_time: int | None = None
    word_count: int | None = None
    created: datetime
    updated: datetime
    loaded: datetime | None = None
    site_name: str | None = None
    image: BookmarkImage | None = None
