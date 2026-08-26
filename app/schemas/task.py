from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None



class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None = None
    project_id: int
    assignee_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SortTaskBy(StrEnum):
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"


class SortOrder(StrEnum):
    DESC = "desc"
    ASC = "asc"
