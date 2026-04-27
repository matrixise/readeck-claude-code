from pydantic import BaseModel


class Label(BaseModel):
    name: str
    count: int | None = None
    href: str | None = None
    href_bookmarks: str | None = None
