from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import APIResponse
from app.db.database import get_db
from app.dependencies.authn import get_current_user
from app.models.user import User
from app.schemas.task import TaskResponse, TaskUpdate, AssignTask
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=APIResponse[TaskResponse])
def get_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = task_service.get_task_by_id(task_id, current_user.id, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, message="Đã thông tin task thành công", data=task
    )


@router.patch("/{task_id}", response_model=APIResponse[TaskResponse])
def update_task(
    task_id: int,
    body: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = task_service.update_task(task_id, current_user.id, body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, data=task, message="Cập nhật task thành công"
    )


@router.delete("/{task_id}", response_model=APIResponse[None])
def delete_task(
    task_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_service.delete_task(task_id, current_user.id, db)
    return APIResponse(statusCode=status.HTTP_200_OK, message="Xóa task thành công")


@router.post("/{task_id}/assign", response_model=APIResponse[TaskResponse])
def assign_task(
    task_id: int,
    body: AssignTask,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = task_service.assign_task(task_id, current_user.id, body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, message="Đã giao task thành công", data=task
    )