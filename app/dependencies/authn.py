from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.exception import AppException
from app.db.database import get_db
from app.models.user import User

credentials = HTTPBearer()


def get_token_claims(
    credentials: HTTPAuthorizationCredentials = Depends(credentials),
):
    token = credentials.credentials
    claims = security.parse_token(token=token)
    return claims


def get_current_user(
    db: Session = Depends(get_db),
    claims: dict[str, str] = Depends(get_token_claims),
):
    user_id = claims.get("sub")
    user = db.get(User, user_id)

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

    return user
