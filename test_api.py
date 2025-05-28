import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing FastAPI E-commerce API")
    print("=============================\n")
    
    # Test user creation
    print("1. Creating test user...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    
    if response.status_code == 200:
        print(f"✅ User created successfully: {response.json()}")
    else:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        if response.status_code == 400 and "already registered" in response.text:
            print("User already exists, continuing with tests...")
        else:
            return
    
    # Test authentication
    print("\n2. Testing authentication...")
    token_response = requests.post(
        f"{BASE_URL}/token", 
        data={"username": user_data["username"], "password": user_data["password"]}
    )
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data["access_token"]
        print(f"✅ Authentication successful, received token")
        
        # Set headers for authenticated requests
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"❌ Authentication failed: {token_response.status_code} - {token_response.text}")
        return
    
    # Test get current user
    print("\n3. Getting current user...")
    user_response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
    
    if user_response.status_code == 200:
        user = user_response.json()
        print(f"✅ Got current user: {user}")
    else:
        print(f"❌ Failed to get current user: {user_response.status_code} - {user_response.text}")
    
    # Test create product
    print("\n4. Creating test products...")
    products = [
        {
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "inventory": 10
        },
        {
            "name": "Smartphone",
            "description": "Latest smartphone model",
            "price": 499.99,
            "inventory": 20
        }
    ]
    
    product_ids = []
    
    for product in products:
        response = requests.post(f"{BASE_URL}/products/", json=product, headers=headers)
        
        if response.status_code == 200:
            product_data = response.json()
            product_ids.append(product_data["id"])
            print(f"✅ Product created: {product_data}")
        else:
            print(f"❌ Failed to create product: {response.status_code} - {response.text}")
    
    if not product_ids:
        print("No products created, fetching existing products...")
        response = requests.get(f"{BASE_URL}/products/")
        if response.status_code == 200:
            for product in response.json():
                product_ids.append(product["id"])
            print(f"Found {len(product_ids)} existing products")
        else:
            print("Failed to get existing products, stopping tests")
            return
    
    # Test get products
    print("\n5. Getting all products...")
    response = requests.get(f"{BASE_URL}/products/")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Retrieved {len(products)} products")
    else:
        print(f"❌ Failed to get products: {response.status_code} - {response.text}")
    
    # Test get product by ID
    print(f"\n6. Getting product with ID {product_ids[0]}...")
    response = requests.get(f"{BASE_URL}/products/{product_ids[0]}")
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Got product: {product}")
    else:
        print(f"❌ Failed to get product: {response.status_code} - {response.text}")
    
    # Test update product
    print(f"\n7. Updating product with ID {product_ids[0]}...")
    updated_product = {
        "name": "Updated Laptop",
        "description": "Updated high-performance laptop",
        "price": 1099.99,
        "inventory": 5
    }
    
    response = requests.put(f"{BASE_URL}/products/{product_ids[0]}", json=updated_product, headers=headers)
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Updated product: {product}")
    else:
        print(f"❌ Failed to update product: {response.status_code} - {response.text}")
    
    # Test create order
    print("\n8. Creating an order...")
    order_data = {
        "customer_id": user["id"],
        "items": [
            {
                "product_id": product_ids[0],
                "quantity": 1,
                "unit_price": 1099.99  # Match the updated price
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
    
    if response.status_code == 200:
        order = response.json()
        order_id = order["id"]
        print(f"✅ Created order: {order}")
    else:
        print(f"❌ Failed to create order: {response.status_code} - {response.text}")
        order_id = None
    
    if order_id:
        # Test get all orders
        print("\n9. Getting all orders...")
        response = requests.get(f"{BASE_URL}/orders/", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Retrieved {len(orders)} orders")
        else:
            print(f"❌ Failed to get orders: {response.status_code} - {response.text}")
        
        # Test get order by ID
        print(f"\n10. Getting order with ID {order_id}...")
        response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Got order: {order}")
        else:
            print(f"❌ Failed to get order: {response.status_code} - {response.text}")
        
        # Test cancel order
        print(f"\n11. Cancelling order with ID {order_id}...")
        response = requests.put(f"{BASE_URL}/orders/{order_id}/cancel", headers=headers)
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Cancelled order: {order}")
        else:
            print(f"❌ Failed to cancel order: {response.status_code} - {response.text}")
    
    if len(product_ids) > 0:
        # Test delete product
        print(f"\n12. Deleting product with ID {product_ids[0]}...")
        response = requests.delete(f"{BASE_URL}/products/{product_ids[0]}", headers=headers)
        
        if response.status_code == 204:
            print(f"✅ Product deleted successfully")
        else:
            print(f"❌ Failed to delete product: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Give the server time to start if run in sequence
    print("Waiting for the server to start...")
    time.sleep(2)
    test_api()
