from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import APIResponse
from app.db.database import get_db
from app.dependencies.authn import get_current_user
from app.dependencies.authr import RequireRole
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me", response_model=APIResponse[UserResponse], status_code=status.HTTP_200_OK
)
def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy thông tin cá nhân thành công",
        data=current_user,
    )


@router.get(
    "", response_model=APIResponse[list[UserResponse]], status_code=status.HTTP_200_OK
)
def list_users(
    keyword: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(RequireRole(["admin"])),
):
    users = user_service.list_users(db, keyword, is_active)
    return APIResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách người dùng thành công",
        data=users,
    )
