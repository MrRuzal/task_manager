from pydantic import BaseModel
from uuid import UUID
from .models import Status


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None
    description: str | None
    status: Status | None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: Status

    model_config = {'from_attributes': True}
