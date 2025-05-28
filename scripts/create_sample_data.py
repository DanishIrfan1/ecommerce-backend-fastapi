#!/usr/bin/env python3
"""
Simplified Demo Data Population Script for E-commerce Admin API
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.models import User, Product, Category, Order, OrderItem, Address
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_sample_data():
    """Create minimal sample data for testing."""
    print("Creating sample data...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin user exists
            result = await db.execute(select(User).where(User.email == "admin@example.com"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                print("Admin user not found, please run create_superuser.py first")
                return
            
            # Create a sample category
            result = await db.execute(select(Category).where(Category.name == "Electronics"))
            category = result.scalar_one_or_none()
            
            if not category:
                category = Category(
                    name="Electronics",
                    description="Electronic devices and accessories"
                )
                db.add(category)
                await db.flush()
                print("  - Created Electronics category")
            
            # Create a sample product
            result = await db.execute(select(Product).where(Product.sku == "TEST-001"))
            product = result.scalar_one_or_none()
            
            if not product:
                product = Product(
                    name="Test Product",
                    description="A test product for demonstration",
                    price=29.99,
                    sku="TEST-001",
                    inventory=100,
                    owner_id=admin_user.id
                )
                product.categories.append(category)
                db.add(product)
                await db.flush()
                print("  - Created test product")
            
            # Create a sample address
            result = await db.execute(select(Address).where(Address.user_id == admin_user.id))
            address = result.scalar_one_or_none()
            
            if not address:
                address = Address(
                    user_id=admin_user.id,
                    address_type="shipping",
                    street_address="123 Test Street",
                    city="Test City",
                    state="TS",
                    country="USA",
                    postal_code="12345",
                    is_default=True
                )
                db.add(address)
                await db.flush()
                print("  - Created test address")
            
            # Create a sample order
            result = await db.execute(select(Order).where(Order.customer_id == admin_user.id))
            order = result.scalar_one_or_none()
            
            if not order:
                order = Order(
                    customer_id=admin_user.id,
                    total_amount=29.99,
                    status="delivered",
                    shipping_address_id=address.id
                )
                db.add(order)
                await db.flush()
                
                # Add order item
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=1,
                    unit_price=29.99
                )
                db.add(order_item)
                print("  - Created test order")
            
            await db.commit()
            print("Sample data creation completed!")
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_sample_data())
