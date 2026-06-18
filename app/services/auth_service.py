from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.core.security import create_access_token, verify_password, hash_password
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from fastapi import HTTPException, status


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    def register(self, user_create: UserCreate) -> User:
        if self.user_repo.get_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        if self.user_repo.get_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user = self.user_repo.create_user(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
        )
        self.activity_repo.log_action(
            user_id=user.id,
            action="register",
            entity_type="user",
            entity_id=user.id,
        )
        return user

    def login(self, user_login: UserLogin) -> str:
        user = self.user_repo.get_by_username(user_login.username)
        if not user or not verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        token = create_access_token(data={"sub": str(user.id)})
        self.activity_repo.log_action(
            user_id=user.id,
            action="login",
            entity_type="user",
            entity_id=user.id,
        )
        return token

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = self.user_repo.get(user_id)
        if not user or not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        user.hashed_password = hash_password(new_password)
        self.db.commit()
        self.activity_repo.log_action(
            user_id=user_id,
            action="change_password",
            entity_type="user",
            entity_id=user_id,
        )

    def get_profile(self, user_id: int) -> User:
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
