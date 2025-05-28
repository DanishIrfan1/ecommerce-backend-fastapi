"""
Tests for product endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


class TestProducts:
    """Test product management endpoints."""

    @pytest.mark.products
    def test_create_product(self, client: TestClient, normal_user_token_headers):
        """Test creating a new product."""
        product_data = {
            "name": "Test Product",
            "description": "A test product for unit testing",
            "price": 99.99,
            "sku": "TEST-001",
            "category_id": 1,
            "stock_quantity": 10
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert content["name"] == product_data["name"]
        assert content["sku"] == product_data["sku"]
        assert content["price"] == product_data["price"]

    @pytest.mark.products
    def test_create_product_unauthorized(self, client: TestClient):
        """Test creating a product without authentication."""
        product_data = {
            "name": "Unauthorized Product",
            "description": "This should fail",
            "price": 50.0,
            "sku": "FAIL-001"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data
        )
        
        assert response.status_code == 401

    @pytest.mark.products
    def test_get_products(self, client: TestClient):
        """Test retrieving products list."""
        response = client.get(f"{settings.API_V1_STR}/products/")
        
        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)

    @pytest.mark.products
    def test_get_product_by_id(self, client: TestClient, normal_user_token_headers):
        """Test retrieving a specific product by ID."""
        # First create a product
        product_data = {
            "name": "Get Test Product",
            "description": "Product for get test",
            "price": 75.0,
            "sku": "GET-001",
            "category_id": 1,
            "stock_quantity": 5
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        assert create_response.status_code == 200
        product_id = create_response.json()["id"]
        
        # Now get the product
        get_response = client.get(f"{settings.API_V1_STR}/products/{product_id}")
        
        assert get_response.status_code == 200
        content = get_response.json()
        assert content["id"] == product_id
        assert content["name"] == product_data["name"]

    @pytest.mark.products
    def test_get_nonexistent_product(self, client: TestClient):
        """Test retrieving a non-existent product."""
        response = client.get(f"{settings.API_V1_STR}/products/99999")
        
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    @pytest.mark.products
    def test_update_product(self, client: TestClient, normal_user_token_headers):
        """Test updating a product."""
        # First create a product
        product_data = {
            "name": "Update Test Product",
            "description": "Product for update test",
            "price": 100.0,
            "sku": "UPDATE-001",
            "category_id": 1,
            "stock_quantity": 8
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        assert create_response.status_code == 200
        product_id = create_response.json()["id"]
        
        # Update the product
        update_data = {
            "name": "Updated Product Name",
            "price": 150.0
        }
        
        update_response = client.put(
            f"{settings.API_V1_STR}/products/{product_id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        assert update_response.status_code == 200
        content = update_response.json()
        assert content["name"] == update_data["name"]
        assert content["price"] == update_data["price"]

    @pytest.mark.products
    def test_delete_product(self, client: TestClient, normal_user_token_headers):
        """Test deleting a product."""
        # First create a product
        product_data = {
            "name": "Delete Test Product",
            "description": "Product for delete test",
            "price": 25.0,
            "sku": "DELETE-001",
            "category_id": 1,
            "stock_quantity": 3
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        assert create_response.status_code == 200
        product_id = create_response.json()["id"]
        
        # Delete the product
        delete_response = client.delete(
            f"{settings.API_V1_STR}/products/{product_id}",
            headers=normal_user_token_headers
        )
        
        assert delete_response.status_code == 200
        
        # Verify the product is deleted
        get_response = client.get(f"{settings.API_V1_STR}/products/{product_id}")
        assert get_response.status_code == 404

    @pytest.mark.products
    def test_search_products(self, client: TestClient, normal_user_token_headers):
        """Test searching products."""
        # Create a product with searchable content
        product_data = {
            "name": "Searchable Test Widget",
            "description": "A unique widget for searching functionality test",
            "price": 45.0,
            "sku": "SEARCH-001",
            "category_id": 1,
            "stock_quantity": 12
        }
        
        client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        # Search for the product
        response = client.get(
            f"{settings.API_V1_STR}/products/?search=Searchable"
        )
        
        assert response.status_code == 200
        content = response.json()
        assert len(content) >= 1
        
        # Check that the search found our product
        found_product = next((p for p in content if p["sku"] == "SEARCH-001"), None)
        assert found_product is not None
        assert "Searchable" in found_product["name"]
