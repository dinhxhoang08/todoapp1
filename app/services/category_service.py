from typing import List
from sqlalchemy.orm import Session
from app.repositories.category_repository import CategoryRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    def create_category(self, user_id: int, category_create: CategoryCreate) -> Category:
        category = Category(
            user_id=user_id,
            name=category_create.name,
            color=category_create.color,
        )
        self.category_repo.create(category)
        self.activity_repo.log_action(
            user_id=user_id,
            action="create",
            entity_type="category",
            entity_id=category.id,
            details=f"Category: {category.name}",
        )
        return category

    def update_category(self, user_id: int, category_id: int, category_update: CategoryUpdate) -> Category:
        category = self.category_repo.get_by_user(user_id, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        self.activity_repo.log_action(
            user_id=user_id,
            action="update",
            entity_type="category",
            entity_id=category.id,
            details=f"Category: {category.name}",
        )
        return category

    def delete_category(self, user_id: int, category_id: int) -> None:
        category = self.category_repo.get_by_user(user_id, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        task_count = self.category_repo.get_task_count(category_id)
        if task_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {task_count} task(s). Reassign tasks first.",
            )
        self.activity_repo.log_action(
            user_id=user_id,
            action="delete",
            entity_type="category",
            entity_id=category.id,
            details=f"Category: {category.name}",
        )
        self.category_repo.delete(category.id)

    def list_categories(self, user_id: int) -> List[Category]:
        categories = self.category_repo.list_by_user(user_id)
        result = []
        for cat in categories:
            cat.task_count = self.category_repo.get_task_count(cat.id)
            result.append(cat)
        return result
