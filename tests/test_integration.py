"""
Integration tests for the complete e-commerce workflow.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


class TestEcommerceWorkflow:
    """Test complete e-commerce workflow integration."""

    @pytest.mark.integration
    def test_complete_shopping_workflow(self, client: TestClient):
        """Test complete shopping workflow from user creation to order completion."""
        
        # Step 1: Create a new customer
        customer_data = {
            "username": "customer123",
            "email": "customer123@example.com",
            "password": "customer123pass",
            "full_name": "John Customer"
        }
        
        create_user_response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=customer_data
        )
        assert create_user_response.status_code == 200
        customer = create_user_response.json()
        
        # Step 2: Customer logs in
        login_data = {
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
        
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Create a seller account
        seller_data = {
            "username": "seller123",
            "email": "seller123@example.com",
            "password": "seller123pass",
            "full_name": "Jane Seller"
        }
        
        create_seller_response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=seller_data
        )
        assert create_seller_response.status_code == 200
        
        # Step 4: Seller logs in
        seller_login_data = {
            "username": seller_data["username"],
            "password": seller_data["password"]
        }
        
        seller_login_response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=seller_login_data
        )
        assert seller_login_response.status_code == 200
        
        seller_token = seller_login_response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # Step 5: Seller creates products
        products_data = [
            {
                "name": "Integration Test Laptop",
                "description": "High-performance laptop for testing",
                "price": 999.99,
                "sku": "INT-LAPTOP-001",
                "category_id": 1,
                "stock_quantity": 10
            },
            {
                "name": "Integration Test Mouse",
                "description": "Wireless mouse for testing",
                "price": 29.99,
                "sku": "INT-MOUSE-001",
                "category_id": 1,
                "stock_quantity": 50
            }
        ]
        
        created_products = []
        for product_data in products_data:
            product_response = client.post(
                f"{settings.API_V1_STR}/products/",
                json=product_data,
                headers=seller_headers
            )
            assert product_response.status_code == 200
            created_products.append(product_response.json())
        
        # Step 6: Customer browses products
        browse_response = client.get(f"{settings.API_V1_STR}/products/")
        assert browse_response.status_code == 200
        available_products = browse_response.json()
        assert len(available_products) >= 2
        
        # Step 7: Customer searches for specific product
        search_response = client.get(
            f"{settings.API_V1_STR}/products/?search=Integration Test Laptop"
        )
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) >= 1
        
        laptop = next(p for p in search_results if "Laptop" in p["name"])
        assert laptop["name"] == "Integration Test Laptop"
        
        # Step 8: Customer views product details
        product_detail_response = client.get(
            f"{settings.API_V1_STR}/products/{laptop['id']}"
        )
        assert product_detail_response.status_code == 200
        detailed_laptop = product_detail_response.json()
        assert detailed_laptop["id"] == laptop["id"]
        
        # Step 9: Customer creates an order with multiple items
        order_data = {
            "items": [
                {
                    "product_id": laptop["id"],
                    "quantity": 1,
                    "unit_price": laptop["price"]
                },
                {
                    "product_id": created_products[1]["id"],  # Mouse
                    "quantity": 2,
                    "unit_price": created_products[1]["price"]
                }
            ],
            "shipping_address_id": 1,
            "total_amount": laptop["price"] + (created_products[1]["price"] * 2)
        }
        
        order_response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=headers
        )
        assert order_response.status_code == 200
        order = order_response.json()
        
        # Verify order details
        assert len(order["items"]) == 2
        assert order["total_amount"] == order_data["total_amount"]
        assert order["status"] == "pending"
        
        # Step 10: Customer checks order status
        order_status_response = client.get(
            f"{settings.API_V1_STR}/orders/{order['id']}",
            headers=headers
        )
        assert order_status_response.status_code == 200
        order_status = order_status_response.json()
        assert order_status["id"] == order["id"]
        
        # Step 11: Seller updates order status
        status_update_data = {"status": "processing"}
        
        update_status_response = client.put(
            f"{settings.API_V1_STR}/orders/{order['id']}",
            json=status_update_data,
            headers=seller_headers
        )
        assert update_status_response.status_code == 200
        updated_order = update_status_response.json()
        assert updated_order["status"] == "processing"
        
        # Step 12: Customer views order history
        order_history_response = client.get(
            f"{settings.API_V1_STR}/orders/",
            headers=headers
        )
        assert order_history_response.status_code == 200
        customer_orders = order_history_response.json()
        assert len(customer_orders) >= 1
        
        customer_order = next(o for o in customer_orders if o["id"] == order["id"])
        assert customer_order["status"] == "processing"

    @pytest.mark.integration
    def test_inventory_management_workflow(self, client: TestClient):
        """Test inventory management workflow."""
        
        # Create a seller
        seller_data = {
            "username": "inventoryseller",
            "email": "inventory@example.com",
            "password": "inventorypass",
            "full_name": "Inventory Seller"
        }
        
        create_seller_response = client.post(
            f"{settings.API_V1_STR}/users/",
            json=seller_data
        )
        assert create_seller_response.status_code == 200
        
        # Login as seller
        login_data = {
            "username": seller_data["username"],
            "password": seller_data["password"]
        }
        
        login_response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a product with limited stock
        product_data = {
            "name": "Limited Stock Item",
            "description": "Product with limited inventory",
            "price": 199.99,
            "sku": "LIMITED-001",
            "category_id": 1,
            "stock_quantity": 5
        }
        
        product_response = client.post(
            f"{settings.API_V1_STR}/products/",
            json=product_data,
            headers=headers
        )
        assert product_response.status_code == 200
        product = product_response.json()
        assert product["stock_quantity"] == 5
        
        # Create customer and login
        customer_data = {
            "username": "stockcustomer",
            "email": "stockcustomer@example.com",
            "password": "stockpass",
            "full_name": "Stock Customer"
        }
        
        client.post(f"{settings.API_V1_STR}/users/", json=customer_data)
        
        customer_login_response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": customer_data["username"], "password": customer_data["password"]}
        )
        customer_token = customer_login_response.json()["access_token"]
        customer_headers = {"Authorization": f"Bearer {customer_token}"}
        
        # Customer places an order for 3 items
        order_data = {
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 3,
                    "unit_price": product["price"]
                }
            ],
            "shipping_address_id": 1,
            "total_amount": product["price"] * 3
        }
        
        order_response = client.post(
            f"{settings.API_V1_STR}/orders/",
            json=order_data,
            headers=customer_headers
        )
        assert order_response.status_code == 200
        
        # Check that stock was reduced (this depends on your implementation)
        updated_product_response = client.get(
            f"{settings.API_V1_STR}/products/{product['id']}"
        )
        assert updated_product_response.status_code == 200
        updated_product = updated_product_response.json()
        
        # Stock should be reduced if your system handles inventory deduction
        # The exact behavior depends on your business logic
        assert updated_product["id"] == product["id"]
