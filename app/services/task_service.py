from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.dashboard import DashboardStats, RecentActivity
from fastapi import HTTPException, status


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.category_repo = CategoryRepository(db)
        self.tag_repo = TagRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    def _log_activity(self, user_id: int, action: str, task: Task):
        self.activity_repo.log_action(
            user_id=user_id,
            action=action,
            entity_type="task",
            entity_id=task.id,
            details=f"Task: {task.title}",
        )

    def create_task(self, user_id: int, task_create: TaskCreate) -> Task:
        task = Task(
            user_id=user_id,
            title=task_create.title,
            description=task_create.description,
            priority=task_create.priority,
            due_date=task_create.due_date,
            category_id=task_create.category_id,
        )
        if task_create.tag_ids:
            tags = self.tag_repo.list_by_user(user_id)
            tag_map = {t.id: t for t in tags}
            task.tags = [tag_map[tid] for tid in task_create.tag_ids if tid in tag_map]
        self.task_repo.create(task)
        self._log_activity(user_id, "create", task)
        return task

    def update_task(self, user_id: int, task_id: int, task_update: TaskUpdate) -> Task:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        update_data = task_update.model_dump(exclude_unset=True)
        if "tag_ids" in update_data and update_data["tag_ids"]:
            tags = self.tag_repo.list_by_user(user_id)
            tag_map = {t.id: t for t in tags}
            task.tags = [tag_map[tid] for tid in update_data.pop("tag_ids") if tid in tag_map]
        for key, value in update_data.items():
            if value is not None:
                setattr(task, key, value)
        if task.status == TaskStatus.completed and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        elif task.status != TaskStatus.completed:
            task.completed_at = None
        self.db.commit()
        self.db.refresh(task)
        self._log_activity(user_id, "update", task)
        return task

    def delete_task(self, user_id: int, task_id: int) -> None:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        self.activity_repo.log_action(
            user_id=user_id,
            action="delete",
            entity_type="task",
            entity_id=task.id,
            details=f"Task: {task.title}",
        )
        self.task_repo.delete(task.id)

    def archive_task(self, user_id: int, task_id: int) -> Task:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        task.status = TaskStatus.archived
        self.db.commit()
        self.db.refresh(task)
        self._log_activity(user_id, "archive", task)
        return task

    def restore_task(self, user_id: int, task_id: int) -> Task:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        task.status = TaskStatus.pending
        self.db.commit()
        self.db.refresh(task)
        self._log_activity(user_id, "restore", task)
        return task

    def complete_task(self, user_id: int, task_id: int) -> Task:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        task.status = TaskStatus.completed
        task.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        self._log_activity(user_id, "complete", task)
        return task

    def duplicate_task(self, user_id: int, task_id: int) -> Task:
        original = self.task_repo.get_by_user(user_id, task_id)
        if not original:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        duplicate = Task(
            user_id=user_id,
            title=f"{original.title} (copy)",
            description=original.description,
            priority=original.priority,
            due_date=original.due_date,
            category_id=original.category_id,
        )
        duplicate.tags = original.tags[:]
        self.task_repo.create(duplicate)
        self._log_activity(user_id, "duplicate", duplicate)
        return duplicate

    def get_task(self, user_id: int, task_id: int) -> Task:
        task = self.task_repo.get_by_user(user_id, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    def list_tasks(
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
        return self.task_repo.list_by_user(
            user_id,
            status=status,
            priority=priority,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            category_id=category_id,
            tag_ids=tag_ids,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        tasks = self.task_repo.list_by_user(user_id, limit=10000)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.completed)
        pending = sum(1 for t in tasks if t.status == TaskStatus.pending)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.in_progress)
        archived = sum(1 for t in tasks if t.status == TaskStatus.archived)
        now = datetime.now(timezone.utc)
        overdue = sum(
            1
            for t in tasks
            if t.due_date and t.due_date < now
            and t.status not in (TaskStatus.completed, TaskStatus.archived)
        )

        tasks_by_status = {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "archived": archived,
        }
        tasks_by_priority = {
            "low": sum(1 for t in tasks if t.priority.value == "low"),
            "medium": sum(1 for t in tasks if t.priority.value == "medium"),
            "high": sum(1 for t in tasks if t.priority.value == "high"),
            "urgent": sum(1 for t in tasks if t.priority.value == "urgent"),
        }
        from app.models.category import Category
        categories = self.db.query(Category).filter(Category.user_id == user_id).all()
        tasks_by_category = {c.name: sum(1 for t in tasks if t.category_id == c.id) for c in categories}

        recent = self.activity_repo.get_recent(user_id, limit=10)
        recent_activity = [
            RecentActivity(
                id=r.id,
                action=r.action,
                entity_type=r.entity_type,
                entity_id=r.entity_id,
                details=r.details,
                created_at=r.created_at,
            )
            for r in recent
        ]

        return DashboardStats(
            total_tasks=total,
            completed_tasks=completed,
            pending_tasks=pending,
            in_progress_tasks=in_progress,
            archived_tasks=archived,
            overdue_tasks=overdue,
            completion_rate=(completed / total * 100) if total > 0 else 0,
            tasks_by_status=tasks_by_status,
            tasks_by_priority=tasks_by_priority,
            tasks_by_category=tasks_by_category,
            recent_activity=recent_activity,
        )
