from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BookmarkResource(BaseModel):
    src: str


class BookmarkResourceImage(BaseModel):
    src: str
    width: int | None = None
    height: int | None = None


class BookmarkResources(BaseModel):
    article: BookmarkResource | None = None
    icon: BookmarkResourceImage | None = None
    image: BookmarkResourceImage | None = None
    thumbnail: BookmarkResourceImage | None = None
    log: BookmarkResource | None = None
    props: BookmarkResource | None = None


class Bookmark(BaseModel):
    id: str
    href: str
    url: str
    title: str
    state: int | None = None
    loaded: bool = False
    type: str | None = None
    document_type: str | None = None
    description: str | None = None
    authors: list[str] = []
    lang: str | None = None
    text_direction: str | None = None
    site_name: str | None = None
    site: str | None = None
    published: datetime | None = None
    has_article: bool = False
    labels: list[str] = []
    is_archived: bool = False
    is_marked: bool = False
    is_deleted: bool = False
    read_progress: int = 0
    reading_time: int | None = None
    word_count: int | None = None
    created: datetime
    updated: datetime
    resources: BookmarkResources | None = None


class BookmarkUpdated(BaseModel):
    id: str
    href: str
    title: str | None = None
    updated: datetime
    is_marked: bool | None = None
    is_archived: bool | None = None
    is_deleted: bool | None = None
    read_progress: int | None = None
    read_anchor: str | None = None
    labels: list[str] | None = None
