from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.exception import AppException
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin


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

    db_refresh_token = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(db_refresh_token)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def refresh_token(refresh_token: str, db: Session):
    claims = security.parse_token(refresh_token)
    user_id = int(claims.get("sub"))
    role = claims.get("role")

    db_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    if not db_token:
        raise AppException(
            message="Token không tồn tại hoặc đã bị thu hồi",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
        )

    db.delete(db_token)
    db.commit()

    access_token = security.generate_token(
        user_id=user_id, duration=settings.ACCESS_EXPIRES_TIME, role=str(role)
    )
    new_refresh_token = security.generate_token(
        user_id=user_id, duration=settings.REFRESH_EXPIRES_TIME, role=str(role)
    )

    new_db_token = RefreshToken(token=new_refresh_token, user_id=user_id)
    db.add(new_db_token)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
