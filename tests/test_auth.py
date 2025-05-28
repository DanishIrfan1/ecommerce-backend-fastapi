"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


class TestAuth:
    """Test authentication endpoints."""

    @pytest.mark.auth
    def test_login_valid_credentials(self, client: TestClient):
        """Test login with valid credentials."""
        # Create a user first
        user_data = {
            "username": "authtest",
            "email": "authtest@example.com",
            "password": "testpass123",
            "full_name": "Auth Test User"
        }
        client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        
        # Test login
        login_data = {
            "username": "authtest",
            "password": "testpass123"
        }
        response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        
        assert response.status_code == 200
        content = response.json()
        assert "access_token" in content
        assert content["token_type"] == "bearer"

    @pytest.mark.auth
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.auth
    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get(f"{settings.API_V1_STR}/users/me/")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.auth
    def test_access_protected_endpoint_with_token(self, client: TestClient, normal_user_token_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get(
            f"{settings.API_V1_STR}/users/me/",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert "username" in content
        assert "email" in content
