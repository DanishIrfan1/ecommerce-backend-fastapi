"""
Test configuration and utilities.
"""

import os
import pytest
from typing import Dict, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database tables."""
    # Remove existing test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    # Clean up test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="module")
def client() -> Generator:
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    """Get superuser authentication headers."""
    # First create a superuser if it doesn't exist
    superuser_data = {
        "username": settings.FIRST_SUPERUSER_USERNAME,
        "email": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
        "full_name": "Super User",
        "is_superuser": True
    }
    client.post(f"{settings.API_V1_STR}/users/", json=superuser_data)
    
    login_data = {
        "username": settings.FIRST_SUPERUSER_USERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    if r.status_code == 200:
        tokens = r.json()
        a_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {a_token}"}
        return headers
    else:
        # Fallback: try to login without creating user
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        tokens = r.json()
        a_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {a_token}"}
        return headers


@pytest.fixture
def normal_user_token_headers(client: TestClient) -> Dict[str, str]:
    """Get normal user authentication headers."""
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    client.post(f"{settings.API_V1_STR}/users/", json=user_data)
    
    # Login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
