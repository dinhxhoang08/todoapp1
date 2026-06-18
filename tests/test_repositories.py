from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.models.tag import Tag


class TestUserRepository:
    def test_create_user(self, db_session):
        repo = UserRepository(db_session)
        user = repo.create_user("newuser", "new@test.com", "password123")
        assert user.id is not None
        assert user.username == "newuser"
        assert user.hashed_password != "password123"

    def test_get_by_username(self, db_session, test_user):
        repo = UserRepository(db_session)
        found = repo.get_by_username("testuser")
        assert found is not None
        assert found.id == test_user.id

    def test_get_by_email(self, db_session, test_user):
        repo = UserRepository(db_session)
        found = repo.get_by_email("test@example.com")
        assert found is not None
        assert found.id == test_user.id

    def test_get_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get(99999) is None


class TestTaskRepository:
    def test_create_task(self, db_session, test_user):
        repo = TaskRepository(db_session)
        task = Task(user_id=test_user.id, title="My task", priority=TaskPriority.high)
        repo.create(task)
        assert task.id is not None
        assert task.title == "My task"

    def test_list_by_user(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        tasks = repo.list_by_user(test_user.id)
        assert len(tasks) >= 1

    def test_list_by_user_filter_status(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        tasks = repo.list_by_user(test_user.id, status="completed")
        assert len(tasks) == 0
        tasks = repo.list_by_user(test_user.id, status="pending")
        assert len(tasks) >= 1

    def test_get_by_user(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        task = repo.get_by_user(test_user.id, test_task.id)
        assert task is not None
        assert task.id == test_task.id

    def test_get_by_user_wrong_user(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        task = repo.get_by_user(99999, test_task.id)
        assert task is None

    def test_update_task(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        updated = repo.update(test_task.id, {"title": "Updated Title"})
        assert updated is not None
        assert updated.title == "Updated Title"

    def test_delete_task(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        repo.delete(test_task.id)
        assert repo.get(test_task.id) is None

    def test_count_by_status(self, db_session, test_user, test_task):
        repo = TaskRepository(db_session)
        stats = repo.count_by_status(test_user.id)
        assert "pending" in stats
        assert stats["pending"] >= 1


class TestCategoryRepository:
    def test_create_and_list(self, db_session, test_user):
        repo = CategoryRepository(db_session)
        cat = Category(user_id=test_user.id, name="Work", color="#ff0000")
        repo.create(cat)
        cats = repo.list_by_user(test_user.id)
        assert len(cats) >= 1
        assert cats[0].name == "Work"

    def test_get_by_user(self, db_session, test_user):
        repo = CategoryRepository(db_session)
        cat = Category(user_id=test_user.id, name="Personal")
        repo.create(cat)
        found = repo.get_by_user(test_user.id, cat.id)
        assert found is not None


class TestTagRepository:
    def test_create_and_list(self, db_session, test_user):
        repo = TagRepository(db_session)
        tag = Tag(user_id=test_user.id, name="important", color="#dc3545")
        repo.create(tag)
        tags = repo.list_by_user(test_user.id)
        assert len(tags) >= 1

    def test_get_by_user(self, db_session, test_user):
        repo = TagRepository(db_session)
        tag = Tag(user_id=test_user.id, name="bug")
        repo.create(tag)
        found = repo.get_by_user(test_user.id, tag.id)
        assert found is not None


class TestActivityLogRepository:
    def test_log_and_recent(self, db_session, test_user):
        repo = ActivityLogRepository(db_session)
        repo.log_action(test_user.id, "test_action", "task", 1, "Test log")
        recent = repo.get_recent(test_user.id)
        assert len(recent) >= 1
        assert recent[0].action == "test_action"
