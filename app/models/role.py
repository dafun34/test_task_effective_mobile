from enum import Enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class PermissionAction(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class BusinessElementName(str, Enum):
    USERS = "users"
    POSTS = "posts"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # admin, user
    description = Column(String(100), nullable=False)  # Администратор, Пользователь

    users = relationship("User", back_populates="role")
    access_rules = relationship("AccessRoleRule", back_populates="role")


class BusinessElement(Base):
    __tablename__ = "business_elements"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # users, products, posts
    description = Column(String(100), nullable=False)  # Пользователи, Товары, посты

    access_rules = relationship("AccessRoleRule", back_populates="element")


class AccessRoleRule(Base):
    __tablename__ = "access_role_rules"

    id = Column(Integer, primary_key=True)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    element_id = Column(Integer, ForeignKey("business_elements.id"), nullable=False)

    read_permission = Column(Boolean, default=False, nullable=False)
    read_all_permission = Column(Boolean, default=False, nullable=False)

    create_permission = Column(Boolean, default=False, nullable=False)

    update_permission = Column(Boolean, default=False, nullable=False)
    update_all_permission = Column(Boolean, default=False, nullable=False)

    delete_permission = Column(Boolean, default=False, nullable=False)
    delete_all_permission = Column(Boolean, default=False, nullable=False)

    role = relationship("Role", back_populates="access_rules")
    element = relationship("BusinessElement", back_populates="access_rules")

    __table_args__ = (UniqueConstraint("role_id", "element_id", name="uq_role_element"),)
