from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import field_validator

from app.core.response import APIResponse


class AppException(Exception):
    def __init__(self, message: str, error: Any, status_code: int) -> None:
        self.status_code = status_code
        self.message = message
        self.error = error


class NotFoundException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "NOT_FOUND", status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "BAD_REQUEST", status.HTTP_400_BAD_REQUEST)


class ForbiddenException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "FORBIDDEN", status.HTTP_403_FORBIDDEN)


def app_exception_handler(_: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            statusCode=exc.status_code, message=exc.message, error=exc.error
        ).model_dump(),
    )

def format_request_validation_errors(
    error: RequestValidationError,
) -> dict[str, str]:
    errors = {}
    for err in error.errors():
        field_name = str(err["loc"][-1])
        message = err["msg"]
        errors[field_name] = message
    return errors

def validate_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=APIResponse(
            statusCode=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="Có lỗi validate",
            error=format_request_validation_errors(exc),
        ).model_dump(),
    )


def internal_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            statusCode=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Lỗi từ phía server",
            error=None,
        ).model_dump(),
    )
