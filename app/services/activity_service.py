from typing import List
from sqlalchemy.orm import Session
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.activity_log import ActivityLog


class ActivityService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_repo = ActivityLogRepository(db)

    def log(self, user_id: int, action: str, entity_type: str = None, entity_id: int = None, details: str = None) -> ActivityLog:
        return self.activity_repo.log_action(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )

    def get_recent(self, user_id: int, limit: int = 10) -> List[ActivityLog]:
        return self.activity_repo.get_recent(user_id, limit=limit)
