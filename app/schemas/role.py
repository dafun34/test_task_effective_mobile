from pydantic import BaseModel, ConfigDict


class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)
