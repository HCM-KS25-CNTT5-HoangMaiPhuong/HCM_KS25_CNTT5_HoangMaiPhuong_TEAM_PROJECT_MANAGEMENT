from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exception import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)
from app.db.database import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(user_id: int, body: ProjectCreate, db: Session):
    new_project = Project(
        name=body.name,
        description=body.description,
        owner_id=user_id,
    )

    db.add(new_project)
    db.flush()
    owner_member = ProjectMember(
        project_id=new_project.id,
        user_id=new_project.owner_id,
        role=ProjectMemberRole.OWNER.value,
    )
    new_project.members.append(owner_member)
    db.commit()
    db.refresh(new_project)
    return new_project


def get_projects(user_id: int, db: Session, name: str | None = None):
    stmt = (
        select(Project)
        .join(ProjectMember, Project.id == ProjectMember.project_id)
        .where(ProjectMember.user_id == user_id)
    )
    if name is not None:
        stmt = stmt.where(Project.name.ilike(f"%{name}%"))

    projects = db.scalars(stmt)
    return projects


def update_project(project: Project, body: ProjectUpdate, db: Session):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException("Cần ít nhất 1 trường để update")
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(project: Project, db: Session):
    db.delete(project)
    db.commit()
    return project


def add_project_member(project_id: int, member_id: int, db: Session):
    member = db.scalar(select(User).where(User.id == member_id, User.is_active == True))
    if not member:
        raise BadRequestException("Nguời dùng không tồn tại")
    member_exists = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == member_id
        )
    )
    if member_exists:
        raise BadRequestException(message="Người dùng đã là thành viên của project")

    new_member = ProjectMember(
        project_id=project_id,
        user_id=member_id,
        role=ProjectMemberRole.MEMBER.value,
    )
    db.add(new_member)
    db.commit()


def delete_project_member(project_id: int, member_id: int, db: Session):
    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.user_id == member_id, ProjectMember.project_id == project_id
        )
    )
    if not member:
        raise NotFoundException(message="Người dùng không phải thành viên của project")
    if member.role == ProjectMemberRole.OWNER.value:
        raise BadRequestException(message="Không thể xóa owner")
    db.delete(member)
    db.commit()


def list_member(project_id: int, db: Session):
    members = db.scalars(
        select(ProjectMember).where(ProjectMember.project_id == project_id)
    )

    return members
