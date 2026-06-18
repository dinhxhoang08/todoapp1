from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        query = self.db.query(self.model)
        if filters:
            for attr, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, attr) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: T) -> T:
        self.db.add(obj_in)
        self.db.commit()
        self.db.refresh(obj_in)
        return obj_in

    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        obj = self.get(id)
        if not obj:
            return None
        for key, value in obj_in.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = self.db.query(self.model)
        if filters:
            for attr, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, attr) == value)
        return query.count()
