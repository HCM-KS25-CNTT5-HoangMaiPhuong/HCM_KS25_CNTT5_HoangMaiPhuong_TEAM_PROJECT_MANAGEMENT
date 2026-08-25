import re

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import APIResponse
from app.db.database import get_db
from app.dependencies.authn import get_current_user
from app.dependencies.authr import require_member, require_owner
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberResponse
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskPriority, TaskResponse, TaskStatus
from app.services import project_service, task_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "", response_model=APIResponse[ProjectResponse], status_code=status.HTTP_201_CREATED
)
def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = project_service.create_project(current_user.id, body, db)
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        data=project,
        message="Đã tạo project thành công",
    )


@router.get(
    "",
    response_model=APIResponse[list[ProjectResponse]],
    status_code=status.HTTP_200_OK,
)
def get_projects(
    name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = project_service.get_projects(current_user.id, db, name)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        data=projects,
        message="Lấy ra danh sách project thành công",
    )


@router.get("/{project_id}", response_model=APIResponse[ProjectResponse])
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_service.get_project_by_id(current_user.id, project_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, data=project, message="Lấy project thành công"
    )


@router.patch("/{project_id}", response_model=APIResponse[ProjectResponse])
def update_project(
    project_id: int,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    project = project_service.update_project(project_id, body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã cập nhật project thành công",
        data=project,
    )


@router.delete("/{project_id}", response_model=APIResponse[ProjectResponse])
def delete_project(
    project_id: int, db: Session = Depends(get_db), _: User = Depends(require_owner)
):
    project = project_service.delete_project(project_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã xóa project thành công",
        data=project,
    )


@router.post(
    "/{project_id}/members",
    response_model=APIResponse[None],
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: int,
    body: ProjectMemberCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    project_service.add_project_member(project_id, body.user_id, db)
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Đã thêm thành viên vào project thành công",
    )


@router.delete("/{project_id}/members/{user_id}", response_model=APIResponse[None])
def delete_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    project_service.delete_project_member(project_id, user_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã xóa thành viên khỏi project thành công",
    )


@router.get(
    "/{project_id}/members", response_model=APIResponse[list[ProjectMemberResponse]]
)
def list_member(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    members = project_service.list_member(current_user.id, project_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        data=members,
        message="Lấy danh sách thành viên của project thành công",
    )


@router.post(
    "/{project_id}/tasks",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_tasks(
    project_id: int,
    body: TaskCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_owner),
):
    task = task_service.create_task(project_id, body, db)
    return APIResponse(
        statusCode=status.HTTP_201_CREATED, message="Đã tạo task", data=task
    )


@router.get("/{project_id}/tasks", response_model=APIResponse[list[TaskResponse]])
def list_tasks(
    project_id: int,
    task_status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee: int | None = None,
    title: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(require_member),
):
    tasks = task_service.list_tasks(
        project_id, db, task_status, priority, assignee, title, limit, offset, sort_by, sort_order
    )
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã lấy danh sách task thành công",
        data=tasks,
    )
