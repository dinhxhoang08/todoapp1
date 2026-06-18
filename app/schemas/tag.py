from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    task_count: Optional[int] = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
