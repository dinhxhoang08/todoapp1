from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.category import Category
from app.models.task import Task


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def list_by_user(self, user_id: int) -> List[Category]:
        return self.db.query(Category).filter(Category.user_id == user_id).all()

    def get_by_user(self, user_id: int, category_id: int) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.id == category_id, Category.user_id == user_id)
            .first()
        )

    def get_task_count(self, category_id: int) -> int:
        return self.db.query(func.count(Task.id)).filter(Task.category_id == category_id).scalar()
