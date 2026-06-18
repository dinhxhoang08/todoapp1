from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    tag_names: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
