from pydantic import BaseModel


class Label(BaseModel):
    id: str
    label: str
    count: int | None = None
