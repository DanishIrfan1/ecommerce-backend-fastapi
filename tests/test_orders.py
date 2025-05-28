"""
Tests for order endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


class TestOrders:
    """Test order management endpoints."""

    @pytest.mark.orders
    def test_create_order(self, client: TestClient, normal_user_token_headers):
        """Test creating a new order."""
        # First create a product to order
        product_data = {
            "name": "Order Test Product",
            "description": "Product for order testing",
            "price": 50.0,
            "sku": "ORDER-PROD-001",
            "category_id": 1,
            "stock_quantity": 100
        }
        
        product_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        assert product_response.status_code == 200
        product_id = product_response.json()["id"]
        
        # Create an order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "unit_price": 50.0
                }
            ],
            "shipping_address_id": 1,
            "total_amount": 100.0
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert content["total_amount"] == order_data["total_amount"]
        assert len(content["items"]) == 1
        assert content["items"][0]["quantity"] == 2

    @pytest.mark.orders
    def test_get_orders(self, client: TestClient, normal_user_token_headers):
        """Test retrieving orders list."""
        response = client.get(
            f"{settings.API_V1_STR}/orders/",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)

    @pytest.mark.orders
    def test_get_order_by_id(self, client: TestClient, normal_user_token_headers):
        """Test retrieving a specific order by ID."""
        # First create a product
        product_data = {
            "name": "Get Order Test Product",
            "description": "Product for get order test",
            "price": 25.0,
            "sku": "GET-ORDER-001",
            "category_id": 1,
            "stock_quantity": 50
        }
        
        product_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        product_id = product_response.json()["id"]
        
        # Create an order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "unit_price": 25.0
                }
            ],
            "shipping_address_id": 1,
            "total_amount": 25.0
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=normal_user_token_headers
        )
        
        assert create_response.status_code == 200
        order_id = create_response.json()["id"]
        
        # Get the order
        get_response = client.get(
            f"{settings.API_V1_STR}/orders/{order_id}",
            headers=normal_user_token_headers
        )
        
        assert get_response.status_code == 200
        content = get_response.json()
        assert content["id"] == order_id
        assert content["total_amount"] == order_data["total_amount"]

    @pytest.mark.orders
    def test_get_nonexistent_order(self, client: TestClient, normal_user_token_headers):
        """Test retrieving a non-existent order."""
        response = client.get(
            f"{settings.API_V1_STR}/orders/99999",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]

    @pytest.mark.orders
    def test_update_order_status(self, client: TestClient, normal_user_token_headers):
        """Test updating order status."""
        # First create a product
        product_data = {
            "name": "Status Update Test Product",
            "description": "Product for status update test",
            "price": 75.0,
            "sku": "STATUS-001",
            "category_id": 1,
            "stock_quantity": 30
        }
        
        product_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=normal_user_token_headers
        )
        
        product_id = product_response.json()["id"]
        
        # Create an order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "unit_price": 75.0
                }
            ],
            "shipping_address_id": 1,
            "total_amount": 75.0
        }
        
        create_response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=normal_user_token_headers
        )
        
        order_id = create_response.json()["id"]
        
        # Update order status
        update_data = {
            "status": "shipped"
        }
        
        update_response = client.put(
            f"{settings.API_V1_STR}/orders/{order_id}",
            json=update_data,
            headers=normal_user_token_headers
        )
        
        assert update_response.status_code == 200
        content = update_response.json()
        assert content["status"] == "shipped"

    @pytest.mark.orders
    def test_create_order_unauthorized(self, client: TestClient):
        """Test creating an order without authentication."""
        order_data = {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 50.0
                }
            ],
            "shipping_address_id": 1,
            "total_amount": 50.0
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data
        )
        
        assert response.status_code == 401

    @pytest.mark.orders
    def test_create_order_invalid_product(self, client: TestClient, normal_user_token_headers):
        """Test creating an order with invalid product ID."""
        order_data = {
            "items": [
                {
                    "product_id": 99999,  # Non-existent product
                    "quantity": 1,
                    "unit_price": 50.0
                }
            ],
            "shipping_address_id": 1,
            "total_amount": 50.0
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=normal_user_token_headers
        )
        
        # This should fail due to foreign key constraint or validation
        assert response.status_code in [400, 422, 404]
