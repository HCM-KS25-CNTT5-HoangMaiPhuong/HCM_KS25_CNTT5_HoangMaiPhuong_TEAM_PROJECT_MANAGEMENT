from __future__ import annotations
from typing import TYPE_CHECKING, List

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.project_member import ProjectMember
    from app.models.task import Task

from app.models.base import Base


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Enum] = mapped_column(
        Enum(UserRole), server_default=text(f"'{UserRole.USER.value}'")
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    owned_projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="owner"
    )
    project_memberships: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="user"
    )
    assigned_tasks: Mapped[list[Task]] = relationship("Task", back_populates="assignee")
