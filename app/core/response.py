from typing import Any

from pydantic import BaseModel


class APIResponse[T](BaseModel):
    statusCode: int
    message: str
    data: T | None = None
    error: Any | None = None
