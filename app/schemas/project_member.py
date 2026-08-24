from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project_member import ProjectMemberRole


class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectMemberUpdate(BaseModel):
    role: ProjectMemberRole


class ProjectMemberResponse(BaseModel):
    project_id: int
    user_id: int
    role: ProjectMemberRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
