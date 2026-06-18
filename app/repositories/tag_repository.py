from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.tag import Tag
from app.models.task_tag import task_tag


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: Session):
        super().__init__(db, Tag)

    def list_by_user(self, user_id: int) -> List[Tag]:
        return self.db.query(Tag).filter(Tag.user_id == user_id).all()

    def get_by_user(self, user_id: int, tag_id: int) -> Optional[Tag]:
        return (
            self.db.query(Tag)
            .filter(Tag.id == tag_id, Tag.user_id == user_id)
            .first()
        )

    def get_task_count(self, tag_id: int) -> int:
        return self.db.query(func.count()).select_from(task_tag).filter(task_tag.c.tag_id == tag_id).scalar()
