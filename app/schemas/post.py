from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    model_config = {"from_attributes": True}


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
