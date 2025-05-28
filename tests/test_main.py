"""
Comprehensive test suite for the Forsit API.

This module contains tests for all API endpoints and functionality.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Dict
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import AsyncSessionLocal, get_db
from app.core.config import settings


# Test configuration
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

TEST_PRODUCT = {
    "name": "Test Product",
    "description": "A test product for API testing",
    "price": 29.99,
    "inventory": 100
}


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing.
    
    Yields:
        AsyncClient: HTTP client for API testing
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_headers(async_client: AsyncClient) -> Dict[str, str]:
    """
    Create authentication headers for testing.
    
    Args:
        async_client: HTTP client
        
    Returns:
        Dict[str, str]: Authorization headers
    """
    # Create a test user
    response = await async_client.post(
        f"{settings.API_V1_STR}/users/",
        json=TEST_USER
    )
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestUsers:
    """Test user-related endpoints."""
    
    async def test_create_user(self, async_client: AsyncClient):
        """Test user creation."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/users/",
            json=user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data
    
    async def test_create_duplicate_user(self, async_client: AsyncClient):
        """Test creating duplicate user fails."""
        response = await async_client.post(
            f"{settings.API_V1_STR}/users/",
            json=TEST_USER
        )
        assert response.status_code == 400
    
    async def test_get_current_user(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting current user information."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == TEST_USER["username"]
        assert data["email"] == TEST_USER["email"]


class TestAuth:
    """Test authentication endpoints."""
    
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful login."""
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "wronguser",
            "password": "wrongpass"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        
        assert response.status_code == 400


class TestProducts:
    """Test product-related endpoints."""
    
    async def test_create_product(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test product creation."""
        response = await async_client.post(
            f"{settings.API_V1_STR}/products/",
            json=TEST_PRODUCT,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == TEST_PRODUCT["name"]
        assert data["price"] == TEST_PRODUCT["price"]
        assert "id" in data
    
    async def test_get_products(self, async_client: AsyncClient):
        """Test getting all products."""
        response = await async_client.get(f"{settings.API_V1_STR}/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_product_by_id(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting a specific product."""
        # First create a product
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/products/",
            json=TEST_PRODUCT,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]
        
        # Then get it
        response = await async_client.get(
            f"{settings.API_V1_STR}/products/{product_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == TEST_PRODUCT["name"]
    
    async def test_update_product(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test updating a product."""
        # Create a product
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/products/",
            json=TEST_PRODUCT,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]
        
        # Update it
        update_data = {"name": "Updated Product", "price": 39.99}
        response = await async_client.put(
            f"{settings.API_V1_STR}/products/{product_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
    
    async def test_delete_product(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test deleting a product."""
        # Create a product
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/products/",
            json=TEST_PRODUCT,
            headers=auth_headers
        )
        product_id = create_response.json()["id"]
        
        # Delete it
        response = await async_client.delete(
            f"{settings.API_V1_STR}/products/{product_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/products/{product_id}"
        )
        assert get_response.status_code == 404


class TestOrders:
    """Test order-related endpoints."""
    
    async def test_create_order(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test order creation."""
        # First create a product
        product_response = await async_client.post(
            f"{settings.API_V1_STR}/products/",
            json=TEST_PRODUCT,
            headers=auth_headers
        )
        product_id = product_response.json()["id"]
        
        # Create an order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
    
    async def test_get_user_orders(self, async_client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting user's orders."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/orders/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSecurity:
    """Test security-related functionality."""
    
    async def test_protected_endpoint_without_auth(self, async_client: AsyncClient):
        """Test accessing protected endpoint without authentication."""
        response = await async_client.get(f"{settings.API_V1_STR}/users/me")
        assert response.status_code == 401
    
    async def test_protected_endpoint_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers=headers
        )
        assert response.status_code == 401


# Utility functions for running tests
def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()
