from typing import List
from sqlalchemy.orm import Session
from app.repositories.tag_repository import TagRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.tag import Tag
from app.schemas.tag import TagCreate
from fastapi import HTTPException, status


class TagService:
    def __init__(self, db: Session):
        self.db = db
        self.tag_repo = TagRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    def create_tag(self, user_id: int, tag_create: TagCreate) -> Tag:
        existing = self.tag_repo.list_by_user(user_id)
        if any(t.name == tag_create.name for t in existing):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists",
            )
        tag = Tag(
            user_id=user_id,
            name=tag_create.name,
            color=tag_create.color,
        )
        self.tag_repo.create(tag)
        self.activity_repo.log_action(
            user_id=user_id,
            action="create",
            entity_type="tag",
            entity_id=tag.id,
            details=f"Tag: {tag.name}",
        )
        return tag

    def delete_tag(self, user_id: int, tag_id: int) -> None:
        tag = self.tag_repo.get_by_user(user_id, tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        self.activity_repo.log_action(
            user_id=user_id,
            action="delete",
            entity_type="tag",
            entity_id=tag.id,
            details=f"Tag: {tag.name}",
        )
        self.tag_repo.delete(tag.id)

    def list_tags(self, user_id: int) -> List[Tag]:
        tags = self.tag_repo.list_by_user(user_id)
        for tag in tags:
            tag.task_count = self.tag_repo.get_task_count(tag.id)
        return tags
