from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exception import ForbiddenException, NotFoundException
from app.db.database import get_db
from app.dependencies.authn import get_current_user, get_token_claims
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.user import User


class RequireRole:
    def __init__(self, allowed_role: list[str]) -> None:
        self.allowed_role = allowed_role

    def __call__(self, claims: dict[str, str] = Depends(get_token_claims)) -> Any:
        if claims.get("role") not in self.allowed_role:
            raise ForbiddenException(
                message="Bạn không có quyền thực hiện thao tác này"
            )
        return claims


def require_owner(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Project, ProjectMember)
        .outerjoin(
            ProjectMember,
            (ProjectMember.project_id == Project.id)
            & (ProjectMember.user_id == current_user.id),
        )
        .where(Project.id == project_id, Project.is_deleted == False)
    )
    result = db.execute(stmt).first()

    if not result:
        raise NotFoundException("Project không tồn tại")

    project, member = result

    if not member or member.role != ProjectMemberRole.OWNER.value:
        raise ForbiddenException("Bạn không có quyền thực hiện thao tác này")

    return project


def require_member(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Project, ProjectMember)
        .outerjoin(
            ProjectMember,
            (ProjectMember.project_id == Project.id)
            & (ProjectMember.user_id == current_user.id),
        )
        .where(Project.id == project_id, Project.is_deleted == False)
    )
    result = db.execute(stmt).first()

    if not result:
        raise NotFoundException("Project không tồn tại")

    project, member = result

    if not member:
        raise ForbiddenException("Bạn không có quyền thực hiện thao tác này")

    return project
