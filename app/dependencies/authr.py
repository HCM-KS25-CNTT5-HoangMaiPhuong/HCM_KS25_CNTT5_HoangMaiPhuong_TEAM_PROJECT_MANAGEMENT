from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exception import ForbiddenException, NotFoundException
from app.db.database import get_db
from app.dependencies.authn import get_current_user, get_token_claims
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.user import User


class RequireRole:
    def __init__(self, allowed_role: list[str]) -> None:
        self.allowed_role = allowed_role

    def __call__(self, claims: dict = Depends(get_token_claims)) -> Any:
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
    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.role == ProjectMemberRole.OWNER.value,
        )
    )

    if not member:
        raise ForbiddenException("Bạn không có quyền thực hiện thao tác này")

    return current_user


def require_member(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )

    if not member:
        raise NotFoundException(message="Không tìm thấy project")

    return current_user
