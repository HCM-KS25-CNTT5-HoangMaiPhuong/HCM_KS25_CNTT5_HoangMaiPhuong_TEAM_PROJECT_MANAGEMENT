import re

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import APIResponse
from app.db.database import get_db
from app.dependencies.authn import get_current_user
from app.dependencies.authr import require_member, require_owner
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberResponse
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskPriority, TaskResponse, TaskStatus
from app.services import project_service, task_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "", 
    response_model=APIResponse[ProjectResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Tạo Project mới",
    description="Tạo một dự án mới. Người tạo sẽ mặc định trở thành OWNER của dự án.",
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
    summary="Lấy danh sách Project",
    description="Lấy danh sách các dự án mà người dùng hiện tại có tham gia (là OWNER hoặc MEMBER). Có thể tìm kiếm theo tên.",
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


@router.get(
    "/{project_id}", 
    response_model=APIResponse[ProjectResponse],
    summary="Chi tiết Project",
    description="Lấy thông tin chi tiết của một dự án thông qua ID.",
)
def get_project_by_id(
    project: Project = Depends(require_member),
):
    return APIResponse(
        statusCode=status.HTTP_200_OK, data=project, message="Lấy project thành công"
    )


@router.patch(
    "/{project_id}", 
    response_model=APIResponse[ProjectResponse],
    summary="Cập nhật Project",
    description="Cập nhật thông tin dự án. Chỉ OWNER mới có quyền thực hiện.",
)
def update_project(
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    project: Project = Depends(require_owner),
):
    project = project_service.update_project(project, body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã cập nhật project thành công",
        data=project,
    )


@router.delete(
    "/{project_id}", 
    response_model=APIResponse[ProjectResponse],
    summary="Xóa Project",
    description="Xóa dự án khỏi hệ thống. Chỉ OWNER mới có quyền thực hiện.",
)
def delete_project(
    db: Session = Depends(get_db), 
    project: Project = Depends(require_owner),
):
    project = project_service.delete_project(project, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã xóa project thành công",
        data=project,
    )


@router.post(
    "/{project_id}/members",
    response_model=APIResponse[None],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên",
    description="Thêm một người dùng vào dự án với vai trò MEMBER. Chỉ OWNER mới có quyền thêm.",
)
def add_project_member(
    project_id: int,
    body: ProjectMemberCreate,
    db: Session = Depends(get_db),
    _: Project = Depends(require_owner),
):
    project_service.add_project_member(project_id, body.user_id, db)
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Đã thêm thành viên vào project thành công",
    )


@router.delete(
    "/{project_id}/members/{user_id}", 
    response_model=APIResponse[None],
    summary="Xóa thành viên",
    description="Xóa một thành viên khỏi dự án. Không thể xóa chính OWNER. Chỉ OWNER mới có quyền xóa.",
)
def delete_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: Project = Depends(require_owner),
):
    project_service.delete_project_member(project_id, user_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã xóa thành viên khỏi project thành công",
    )


@router.get(
    "/{project_id}/members", 
    response_model=APIResponse[list[ProjectMemberResponse]],
    summary="Danh sách thành viên",
    description="Lấy danh sách các thành viên trong dự án.",
)
def list_member(
    project_id: int,
    db: Session = Depends(get_db),
    _: Project = Depends(require_member),
):
    members = project_service.list_member(project_id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        data=members,
        message="Lấy danh sách thành viên của project thành công",
    )


@router.post(
    "/{project_id}/tasks",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo Task mới",
    description="Tạo một task mới trong dự án. Chỉ OWNER của dự án mới có quyền tạo.",
)
def create_tasks(
    project_id: int,
    body: TaskCreate,
    db: Session = Depends(get_db),
    _: Project = Depends(require_owner),
):
    task = task_service.create_task(project_id, body, db)
    return APIResponse(
        statusCode=status.HTTP_201_CREATED, message="Đã tạo task", data=task
    )


@router.get(
    "/{project_id}/tasks", 
    response_model=APIResponse[list[TaskResponse]],
    summary="Danh sách Task",
    description="Lấy danh sách task của dự án. Hỗ trợ phân trang, tìm kiếm và sắp xếp.",
)
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
    _: Project = Depends(require_member),
):
    tasks = task_service.list_tasks(
        project_id, db, task_status, priority, assignee, title, limit, offset, sort_by, sort_order
    )
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Đã lấy danh sách task thành công",
        data=tasks,
    )
