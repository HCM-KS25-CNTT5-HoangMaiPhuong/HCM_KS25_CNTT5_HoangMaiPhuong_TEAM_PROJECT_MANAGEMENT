from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exception import BadRequestException, NotFoundException
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
        print(name)

        stmt = stmt.where(Project.name.ilike(f"%{name}%"))

    projects = db.scalars(stmt)
    return projects


def get_project_by_id(user_id: int, project_id: int, db: Session):
    stmt = (
        select(Project)
        .join(
            ProjectMember,
            (ProjectMember.project_id == Project.id)
            & (ProjectMember.user_id == user_id),
        )
        .where(Project.id == project_id)
    )
    project = db.scalar(stmt)
    if not project:
        raise NotFoundException(message="Không tìm thấy Project")

    return project


def update_project(project_id: int, body: ProjectUpdate, db: Session):
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise NotFoundException("Project không tồn tại")
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise BadRequestException("Cần it nhất 1 trường để update")
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    return project


def delete_project(project_id: int, db: Session):
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise NotFoundException("Project không tồn tại")
    db.delete(project)
    db.commit()
    return project


def add_project_member(project_id: int, member_id: int, db: Session):
    member_exists = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == member_id
        )
    )
    if member_exists:
        raise BadRequestException(message="Người dùng đã là thành viên của project")
    member = db.scalar(select(User).where(User.id == member_id))
    if not member:
        raise BadRequestException("Nguời dùng không tồn tại")
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
