from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.activity_log import ActivityLog


class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self, db: Session):
        super().__init__(db, ActivityLog)

    def log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str = None,
        entity_id: int = None,
        details: str = None,
    ) -> ActivityLog:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_recent(self, user_id: int, limit: int = 10) -> List[ActivityLog]:
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
