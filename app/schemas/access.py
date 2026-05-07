from pydantic import BaseModel


class AccessRuleUpdate(BaseModel):
    read_permission: bool | None = None
    read_all_permission: bool | None = None

    create_permission: bool | None = None

    update_permission: bool | None = None
    update_all_permission: bool | None = None

    delete_permission: bool | None = None
    delete_all_permission: bool | None = None


class RoleShortRead(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


class BusinessElementShortRead(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


class AccessRuleRead(BaseModel):
    id: int
    role: RoleShortRead
    element: BusinessElementShortRead

    read_permission: bool
    read_all_permission: bool
    create_permission: bool
    update_permission: bool
    update_all_permission: bool
    delete_permission: bool
    delete_all_permission: bool

    model_config = {"from_attributes": True}
