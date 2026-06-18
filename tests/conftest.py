import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database.session import Base
from app.models.user import User
from app.core.security import hash_password, create_access_token
from app.core.dependencies import get_db
from starlette.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Cookie": f"access_token={token}"}


@pytest.fixture(scope="function")
def test_task(db_session, test_user):
    from app.models.task import Task, TaskStatus, TaskPriority
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.pending,
        priority=TaskPriority.medium,
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task
