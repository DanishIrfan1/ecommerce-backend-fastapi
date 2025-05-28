"""
Tests for user endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


class TestUsers:
    """Test user management endpoints."""

    @pytest.mark.users
    def test_create_user(self, client: TestClient):
        """Test creating a new user."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        
        assert response.status_code == 200
        content = response.json()
        assert content["username"] == user_data["username"]
        assert content["email"] == user_data["email"]
        assert content["full_name"] == user_data["full_name"]
        assert "password" not in content  # Password should not be returned

    @pytest.mark.users
    def test_create_user_duplicate_username(self, client: TestClient):
        """Test creating a user with duplicate username."""
        user_data = {
            "username": "duplicate",
            "email": "duplicate1@example.com",
            "password": "password123",
            "full_name": "Duplicate User 1"
        }
        
        # Create first user
        response1 = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        assert response1.status_code == 200
        
        # Try to create second user with same username
        user_data2 = {
            "username": "duplicate",  # Same username
            "email": "duplicate2@example.com",  # Different email
            "password": "password123",
            "full_name": "Duplicate User 2"
        }
        
        response2 = client.post(f"{settings.API_V1_STR}/users/", json=user_data2)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

    @pytest.mark.users
    def test_create_user_duplicate_email(self, client: TestClient):
        """Test creating a user with duplicate email."""
        user_data = {
            "username": "emaildup1",
            "email": "emaildup@example.com",
            "password": "password123",
            "full_name": "Email Duplicate User 1"
        }
        
        # Create first user
        response1 = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        assert response1.status_code == 200
        
        # Try to create second user with same email
        user_data2 = {
            "username": "emaildup2",  # Different username
            "email": "emaildup@example.com",  # Same email
            "password": "password123",
            "full_name": "Email Duplicate User 2"
        }
        
        response2 = client.post(f"{settings.API_V1_STR}/users/", json=user_data2)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

    @pytest.mark.users
    def test_get_current_user(self, client: TestClient, normal_user_token_headers):
        """Test getting current user information."""
        response = client.get(
            f"{settings.API_V1_STR}/users/me/",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert "username" in content
        assert "email" in content
        assert "id" in content

    @pytest.mark.users
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get(f"{settings.API_V1_STR}/users/me/")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.users
    def test_update_current_user(self, client: TestClient, normal_user_token_headers):
        """Test updating current user information."""
        update_data = {
            "full_name": "Updated Full Name",
            "email": "updated@example.com"
        }
        
        response = client.put(
            f"{settings.API_V1_STR}/users/me/",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert content["full_name"] == update_data["full_name"]
        assert content["email"] == update_data["email"]

    @pytest.mark.users
    def test_create_user_invalid_email(self, client: TestClient):
        """Test creating a user with invalid email format."""
        user_data = {
            "username": "invalidemail",
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Invalid Email User"
        }
        
        response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.users
    def test_create_user_weak_password(self, client: TestClient):
        """Test creating a user with a weak password."""
        user_data = {
            "username": "weakpass",
            "email": "weakpass@example.com",
            "password": "123",  # Too short
            "full_name": "Weak Password User"
        }
        
        response = client.post(f"{settings.API_V1_STR}/users/", json=user_data)
        
        # This might be 422 (validation error) or 400 depending on implementation
        assert response.status_code in [400, 422]
