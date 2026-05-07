from pydantic import BaseModel, EmailStr, ConfigDict

from app.schemas.role import RoleOut


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    password_repeat: str
    first_name: str
    last_name: str | None = None
    middle_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str | None
    middle_name: str | None
    role: RoleOut | None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
