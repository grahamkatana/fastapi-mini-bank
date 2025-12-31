import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import Settings

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_settings():
    """Override settings for testing"""
    return Settings(
        DATABASE_URL=SQLALCHEMY_DATABASE_URL,
        SECRET_KEY="test-secret-key-for-testing-only",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        CELERY_BROKER_URL="redis://localhost:6379/0",
        CELERY_RESULT_BACKEND="redis://localhost:6379/0",
        APP_NAME="FastAPI Test",
        DEBUG=True
    )


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden dependencies"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }


@pytest.fixture
def test_user(client, test_user_data):
    """Create a test user and return user data"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return test_user_data


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_account(client, auth_headers):
    """Create a test account and return account data"""
    account_data = {
        "account_type": "savings",
        "currency": "USD"
    }
    response = client.post(
        "/api/v1/accounts/",
        json=account_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()
