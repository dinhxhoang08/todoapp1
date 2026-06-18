from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class RecentActivity(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime


class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    archived_tasks: int
    overdue_tasks: int
    completion_rate: float
    tasks_by_status: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    tasks_by_category: Dict[str, int]
    recent_activity: List[RecentActivity]
