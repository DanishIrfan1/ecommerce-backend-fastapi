#!/usr/bin/env python3
"""
Demo Data Population Script for E-commerce Admin API

This script populates the database with sample data representing
products sold on Amazon & Walmart for demonstration purposes.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.models import User, Product, Category, Order, OrderItem, Address
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# Sample product data inspired by Amazon & Walmart categories
SAMPLE_CATEGORIES = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
    {"name": "Clothing & Apparel", "description": "Fashion and clothing items"},
    {"name": "Books & Media", "description": "Books, movies, and digital media"},
    {"name": "Sports & Outdoors", "description": "Sports equipment and outdoor gear"},
    {"name": "Health & Beauty", "description": "Health, beauty, and personal care"},
    {"name": "Automotive", "description": "Automotive parts and accessories"},
    {"name": "Toys & Games", "description": "Toys, games, and children's items"},
]

SAMPLE_PRODUCTS = [
    # Electronics
    {"name": "Wireless Bluetooth Headphones", "sku": "WBH-001", "price": 79.99, "inventory": 150, "category": "Electronics", "description": "High-quality wireless headphones with noise cancellation"},
    {"name": "4K Smart TV 55 inch", "sku": "TV-4K-55", "price": 499.99, "inventory": 25, "category": "Electronics", "description": "Ultra HD Smart TV with streaming capabilities"},
    {"name": "Smartphone Case", "sku": "SPC-001", "price": 19.99, "inventory": 300, "category": "Electronics", "description": "Protective case for smartphones"},
    {"name": "Laptop Stand Adjustable", "sku": "LS-ADJ", "price": 45.99, "inventory": 80, "category": "Electronics", "description": "Ergonomic laptop stand with adjustable height"},
    
    # Home & Garden
    {"name": "Coffee Maker 12-Cup", "sku": "CM-12C", "price": 89.99, "inventory": 60, "category": "Home & Garden", "description": "Programmable coffee maker with thermal carafe"},
    {"name": "Garden Hose 50ft", "sku": "GH-50", "price": 34.99, "inventory": 120, "category": "Home & Garden", "description": "Heavy-duty garden hose with spray nozzle"},
    {"name": "LED Desk Lamp", "sku": "LED-DL", "price": 42.99, "inventory": 90, "category": "Home & Garden", "description": "Energy-efficient LED desk lamp with adjustable brightness"},
    
    # Clothing & Apparel
    {"name": "Men's Cotton T-Shirt", "sku": "MCT-001", "price": 24.99, "inventory": 200, "category": "Clothing & Apparel", "description": "100% cotton comfortable t-shirt"},
    {"name": "Women's Running Shoes", "sku": "WRS-001", "price": 89.99, "inventory": 75, "category": "Clothing & Apparel", "description": "Lightweight running shoes with cushioned sole"},
    {"name": "Denim Jeans Classic", "sku": "DJ-CLS", "price": 59.99, "inventory": 100, "category": "Clothing & Apparel", "description": "Classic fit denim jeans"},
    
    # Books & Media
    {"name": "Programming Book - Python", "sku": "PB-PY", "price": 39.99, "inventory": 40, "category": "Books & Media", "description": "Comprehensive Python programming guide"},
    {"name": "Bluetooth Speaker Portable", "sku": "BSP-001", "price": 29.99, "inventory": 110, "category": "Books & Media", "description": "Portable Bluetooth speaker with excellent sound quality"},
    
    # Sports & Outdoors
    {"name": "Yoga Mat Premium", "sku": "YM-PREM", "price": 34.99, "inventory": 85, "category": "Sports & Outdoors", "description": "Non-slip premium yoga mat"},
    {"name": "Water Bottle Insulated", "sku": "WB-INS", "price": 24.99, "inventory": 180, "category": "Sports & Outdoors", "description": "Stainless steel insulated water bottle"},
    {"name": "Camping Tent 4-Person", "sku": "CT-4P", "price": 129.99, "inventory": 30, "category": "Sports & Outdoors", "description": "Waterproof 4-person camping tent"},
    
    # Health & Beauty
    {"name": "Electric Toothbrush", "sku": "ETB-001", "price": 49.99, "inventory": 70, "category": "Health & Beauty", "description": "Rechargeable electric toothbrush with multiple modes"},
    {"name": "Vitamin C Supplement", "sku": "VCS-001", "price": 19.99, "inventory": 150, "category": "Health & Beauty", "description": "High-potency Vitamin C dietary supplement"},
    
    # Automotive
    {"name": "Car Phone Mount", "sku": "CPM-001", "price": 16.99, "inventory": 95, "category": "Automotive", "description": "Universal car phone mount with secure grip"},
    {"name": "Motor Oil 5W-30", "sku": "MO-5W30", "price": 24.99, "inventory": 200, "category": "Automotive", "description": "Synthetic blend motor oil 5 quart"},
    
    # Toys & Games
    {"name": "Board Game Strategy", "sku": "BGS-001", "price": 44.99, "inventory": 50, "category": "Toys & Games", "description": "Strategic board game for family fun"},
    {"name": "Educational Puzzle 1000pc", "sku": "EP-1000", "price": 18.99, "inventory": 65, "category": "Toys & Games", "description": "1000-piece educational jigsaw puzzle"},
]

SAMPLE_USERS = [
    {"username": "admin", "email": "admin@forsit.com", "password": "admin123", "is_superuser": True},
    {"username": "manager", "email": "manager@forsit.com", "password": "manager123", "is_superuser": False},
    {"username": "customer1", "email": "customer1@example.com", "password": "customer123", "is_superuser": False},
    {"username": "customer2", "email": "customer2@example.com", "password": "customer123", "is_superuser": False},
    {"username": "customer3", "email": "customer3@example.com", "password": "customer123", "is_superuser": False},
]

SAMPLE_ADDRESSES = [
    {"street_address": "123 Main St", "city": "New York", "state": "NY", "country": "USA", "postal_code": "10001", "address_type": "shipping"},
    {"street_address": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "country": "USA", "postal_code": "90210", "address_type": "shipping"},
    {"street_address": "789 Pine Rd", "city": "Chicago", "state": "IL", "country": "USA", "postal_code": "60601", "address_type": "shipping"},
    {"street_address": "321 Elm St", "city": "Houston", "state": "TX", "country": "USA", "postal_code": "77001", "address_type": "shipping"},
    {"street_address": "654 Maple Dr", "city": "Phoenix", "state": "AZ", "country": "USA", "postal_code": "85001", "address_type": "shipping"},
]


async def create_categories(db: AsyncSession) -> dict:
    """Create sample categories."""
    categories = {}
    print("Creating categories...")
    
    for cat_data in SAMPLE_CATEGORIES:
        # Check if category already exists
        result = await db.execute(select(Category).where(Category.name == cat_data["name"]))
        existing_category = result.scalar_one_or_none()
        
        if existing_category:
            categories[cat_data["name"]] = existing_category
            print(f"  - Category already exists: {cat_data['name']}")
        else:
            category = Category(**cat_data)
            db.add(category)
            await db.flush()
            categories[cat_data["name"]] = category
            print(f"  - Created category: {cat_data['name']}")
    
    await db.commit()
    return categories


async def create_users(db: AsyncSession) -> list:
    """Create sample users."""
    users = []
    print("Creating users...")
    
    for user_data in SAMPLE_USERS:
        # Check if user already exists
        result = await db.execute(select(User).where(User.username == user_data["username"]))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            users.append(existing_user)
            print(f"  - User already exists: {user_data['username']}")
        else:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                is_superuser=user_data["is_superuser"],
                is_active=True
            )
            db.add(user)
            await db.flush()
            users.append(user)
            print(f"  - Created user: {user_data['username']} ({'superuser' if user_data['is_superuser'] else 'user'})")
    
    await db.commit()
    return users


async def create_addresses(db: AsyncSession, users: list) -> None:
    """Create sample addresses for users."""
    print("Creating addresses...")
    
    for i, addr_data in enumerate(SAMPLE_ADDRESSES):
        if i < len(users):
            address = Address(
                user_id=users[i].id,
                is_default=True,
                **addr_data
            )
            db.add(address)
            print(f"  - Created address for {users[i].username}")
    
    await db.commit()


async def create_products(db: AsyncSession, categories: dict) -> list:
    """Create sample products."""
    products = []
    print("Creating products...")
    
    for prod_data in SAMPLE_PRODUCTS:
        # Check if product already exists
        result = await db.execute(select(Product).where(Product.sku == prod_data["sku"]))
        existing_product = result.scalar_one_or_none()
        
        if existing_product:
            products.append(existing_product)
            print(f"  - Product already exists: {prod_data['name']} (SKU: {prod_data['sku']})")
        else:
            # Get admin user as owner
            result = await db.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                print("Error: Admin user not found. Please create admin user first.")
                continue
            
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                price=prod_data["price"],
                sku=prod_data["sku"],
                inventory=prod_data["inventory"],
                owner_id=admin_user.id
            )
            
            # Add category relationship
            category = categories.get(prod_data["category"])
            if category:
                product.categories.append(category)
            
            db.add(product)
            await db.flush()
            products.append(product)
            print(f"  - Created product: {prod_data['name']} (SKU: {prod_data['sku']})")
    
    await db.commit()
    return products


async def create_orders(db: AsyncSession, users: list, products: list) -> None:
    """Create sample orders with realistic sales data."""
    print("Creating orders and sales data...")
    
    # Create orders for the past 12 months
    start_date = datetime.now() - timedelta(days=365)
    
    order_count = 0
    for days_back in range(0, 365, random.randint(1, 7)):  # Random frequency
        order_date = start_date + timedelta(days=days_back)
        
        # Create 1-5 orders per week
        for _ in range(random.randint(1, 5)):
            # Random customer (excluding admin users)
            customer = random.choice([u for u in users if not u.is_superuser])
            
            # Calculate total amount first
            total_amount = 0.0
            order_items_data = []
            
            # Prepare order items
            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                unit_price = float(product.price)
                
                order_items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
                total_amount += unit_price * quantity
            
            order = Order(
                customer_id=customer.id,  # Fixed: use customer_id instead of user_id
                total_amount=total_amount,
                status=random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                order_date=order_date  # Fixed: use order_date instead of created_at
            )
            db.add(order)
            await db.flush()
            
            # Add order items
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product'].id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                db.add(order_item)
                
                # Update product inventory
                if item_data['product'].inventory >= item_data['quantity']:
                    item_data['product'].inventory -= item_data['quantity']
            
            order_count += 1
    
    await db.commit()
    print(f"  - Created {order_count} orders with realistic sales data")


async def populate_demo_data():
    """Main function to populate all demo data."""
    print("Starting demo data population...")
    print("=" * 50)
    
    async with AsyncSessionLocal() as db:
        try:
            # Create all demo data
            categories = await create_categories(db)
            users = await create_users(db)
            await create_addresses(db, users)
            products = await create_products(db, categories)
            await create_orders(db, users, products)
            
            print("=" * 50)
            print("Demo data population completed successfully!")
            print(f"Created:")
            print(f"  - {len(SAMPLE_CATEGORIES)} categories")
            print(f"  - {len(SAMPLE_USERS)} users")
            print(f"  - {len(SAMPLE_ADDRESSES)} addresses")
            print(f"  - {len(SAMPLE_PRODUCTS)} products")
            print(f"  - Multiple orders with sales history")
            print()
            print("Admin credentials:")
            print("  Username: admin")
            print("  Password: admin123")
            print()
            print("Manager credentials:")
            print("  Username: manager")
            print("  Password: manager123")
            
        except Exception as e:
            print(f"Error populating demo data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(populate_demo_data())
