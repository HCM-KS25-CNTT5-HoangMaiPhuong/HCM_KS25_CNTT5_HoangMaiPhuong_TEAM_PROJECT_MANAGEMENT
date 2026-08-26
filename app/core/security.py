from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import status

from app.core.config import settings
from app.core.exception import AppException


def hash_password(password: str):
    salt = bcrypt.gensalt()
    bytes_password = password.encode()
    return bcrypt.hashpw(bytes_password, salt).decode()


def verify_password(password: str, hashed_password: str):
    bytes_password = password.encode()
    bytes_hashed_password = hashed_password.encode()
    return bcrypt.checkpw(bytes_password, bytes_hashed_password)


def generate_token(user_id: int, duration: int, role: str):
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "role": role,
        "exp": now + timedelta(minutes=duration),
    }
    return jwt.encode(payload=claims, key=settings.SECRET_KEY, algorithm="HS256")


def parse_token(token: str):
    try:
        claims = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        return claims

    except jwt.ExpiredSignatureError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token hết hạn",
            error="UNAUTHORIZED",
        )

    except jwt.InvalidTokenError:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token không hợp lệ",
            error="UNAUTHORIZED",
        )
