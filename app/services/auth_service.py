from venv import create

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import status
from app.core import security
from app.core.config import settings
from app.core.exception import AppException
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse


def register(body: UserCreate, db: Session):
    email_exists = db.scalar(select(User.email).where(User.email == body.email))
    if email_exists:
        raise AppException(
            message="Email đã tồn tại",
            status_code=status.HTTP_409_CONFLICT,
            error="CONFLICT",
        )

    hashed_password = security.hash_password(body.password)
    new_user = User(
        email=body.email, password_hash=hashed_password, full_name=body.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login(body: UserLogin, db: Session):
    user = db.scalar(select(User).where(User.email == body.email))
    if not user:
        raise AppException(
            message="Thông tin đăng nhập không hợp lệ",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
        )
    if not user.is_active:
        raise AppException(
            message="Tài khoản đã bị vô hiệu hóa",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
        )
    matched_password = security.verify_password(body.password, user.password_hash)
    if not matched_password:
        raise AppException(
            message="Thông tin đăng nhập không hợp lệ",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
        )
    access_token = security.generate_token(
        user_id=user.id, duration=settings.ACCESS_EXPIRES_TIME, role=str(user.role)
    )
    refresh_token = security.generate_token(
        user_id=user.id, duration=settings.REFRESH_EXPIRES_TIME, role=str(user.role)
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
