from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.core.exception import (
    AppException,
    app_exception_handler,
    internal_exception_handler,
    sqlalchemy_integrity_exception_handler,
    validate_exception_handler,
)
from app.core.response import APIResponse
from app.db.database import engine
from app.models import Base
from app.routers import auth, projects, tasks, users

app = FastAPI()
Base.metadata.create_all(bind=engine)


app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validate_exception_handler)  # type: ignore  # type: ignore
app.add_exception_handler(IntegrityError, sqlalchemy_integrity_exception_handler)  # type: ignore  # type: ignore
app.add_exception_handler(Exception, internal_exception_handler)  # type: ignore

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/", response_model=APIResponse[None], tags=["health"])
def check_health():
    return APIResponse(statusCode=status.HTTP_200_OK, message="Server đang chạy")
