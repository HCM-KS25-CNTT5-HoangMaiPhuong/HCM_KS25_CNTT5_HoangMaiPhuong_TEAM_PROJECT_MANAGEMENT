from anyio.functools import S
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import APIResponse
from app.db.database import get_db
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
    description="Tạo một tài khoản người dùng mới trong hệ thống bằng email và mật khẩu.",
)
def register(body: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.register(body, db)
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        data=user,
        message="Đăng kí thành công",
    )


@router.post(
    "/login", 
    response_model=APIResponse[TokenResponse], 
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập",
    description="Đăng nhập vào hệ thống để lấy Access Token và Refresh Token.",
)
def login(body: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.login(body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, message="Đăng nhập thành công", data=token
    )
