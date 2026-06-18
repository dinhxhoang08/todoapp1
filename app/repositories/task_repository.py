from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories.base import BaseRepository
from app.models.task import Task, TaskStatus


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(db, Task)

    def list_by_user(
        self,
        user_id: int,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        category_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 50,
    ) -> List[Task]:
        query = self.db.query(Task).filter(Task.user_id == user_id)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if due_date_from:
            query = query.filter(Task.due_date >= due_date_from)
        if due_date_to:
            query = query.filter(Task.due_date <= due_date_to)
        if category_id:
            query = query.filter(Task.category_id == category_id)
        if tag_ids:
            from app.models.task_tag import task_tag
            query = query.filter(
                Task.id.in_(
                    self.db.query(task_tag.c.task_id).filter(
                        task_tag.c.tag_id.in_(tag_ids)
                    )
                )
            )
        if search_query:
            like = f"%{search_query}%"
            query = query.filter(
                or_(Task.title.ilike(like), Task.description.ilike(like))
            )

        sort_col = getattr(Task, sort_by, Task.created_at)
        sort_method = sort_col.desc() if sort_order == "desc" else sort_col.asc()
        query = query.order_by(sort_method)

        return query.offset(skip).limit(limit).all()

    def get_by_user(self, user_id: int, task_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    def get_overdue(self, user_id: int) -> List[Task]:
        now = datetime.utcnow()
        return (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != TaskStatus.completed,
                Task.status != TaskStatus.archived,
            )
            .all()
        )

    def get_completion_stats(self, user_id: int) -> Dict[str, Any]:
        total = self.count({"user_id": user_id})
        completed = self.count({"user_id": user_id, "status": TaskStatus.completed.value})
        return {
            "total": total,
            "completed": completed,
            "rate": (completed / total * 100) if total > 0 else 0,
        }

    def count_by_status(self, user_id: int) -> Dict[str, int]:
        from sqlalchemy import func
        result = {}
        rows = (
            self.db.query(Task.status, func.count(Task.id))
            .filter(Task.user_id == user_id)
            .group_by(Task.status)
            .all()
        )
        for status, count in rows:
            result[status] = count
        for s in TaskStatus:
            if s.value not in result:
                result[s.value] = 0
        return result

    def count_by_priority(self, user_id: int) -> Dict[str, int]:
        from sqlalchemy import func
        result = {}
        rows = (
            self.db.query(Task.priority, func.count(Task.id))
            .filter(Task.user_id == user_id)
            .group_by(Task.priority)
            .all()
        )
        for priority, count in rows:
            result[priority] = count
        return result
