from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exception import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models import ProjectMember, Task
from app.models.project_member import ProjectMemberRole
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(project_id: int, body: TaskCreate, db: Session):

    new_task = Task(**body.model_dump())
    new_task.project_id = project_id
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_task_by_id(task_id: int, user_id: int, db: Session):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise NotFoundException(message="Không tồn tại tại task")

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if not member:
        raise ForbiddenException(message="Bạn không có quyền xem task này")

    return task


def update_task(task_id: int, user_id: int, body: TaskUpdate, db: Session):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise NotFoundException(message="Không tồn tại tại task")

    owner = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.OWNER.value,
        )
    )
    if not owner:
        raise ForbiddenException(message="Chỉ OWNER mới có quyền cập nhật task")

    if body.assignee_id is not None:
        assignee = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == body.assignee_id,
            )
        )
        if not assignee:
            raise BadRequestException(
                message="Người được giao không phải là thành viên của project"
            )

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    return task


def delete_task(task_id: int, user_id: int, db: Session):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise NotFoundException(message="Không tồn tại task này")

    owner = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == ProjectMemberRole.OWNER.value,
        )
    )
    if not owner:
        raise ForbiddenException(message="Chỉ OWNER mới có quyền xóa task")

    db.delete(task)
    db.commit()



def list_tasks(
    project_id: int,
    db: Session,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee: int | None = None,
    title: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    stmt = select(Task).where(Task.project_id == project_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)

    if priority is not None:
        stmt = stmt.where(Task.priority == priority)

    if assignee is not None:
        stmt = stmt.where(Task.assignee_id == assignee)

    if title:
        stmt = stmt.where(Task.title.ilike(f"%{title}%"))

    if sort_by == "due_date":
        stmt = stmt.order_by(
            Task.due_date.asc() if sort_order == "asc" else Task.due_date.desc()
        )
    else:
        stmt = stmt.order_by(
            Task.created_at.asc() if sort_order == "asc" else Task.created_at.desc()
        )

    stmt = stmt.offset(offset).limit(limit)
    tasks = db.scalars(stmt)
    return tasks
