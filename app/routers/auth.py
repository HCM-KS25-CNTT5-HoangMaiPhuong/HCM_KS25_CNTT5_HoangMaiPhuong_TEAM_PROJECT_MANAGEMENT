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
)
def register(body: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.register(body, db)
    
    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        data=user,
        message="Đăng kí thành công",
    )


@router.post(
    "/login", response_model=APIResponse[TokenResponse], status_code=status.HTTP_200_OK
)
def login(body: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.login(body, db)
    return APIResponse(
        statusCode=status.HTTP_200_OK, message="Đăng nhập thành công", data=token
    )
