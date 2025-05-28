"""
API router configuration.

Collects all API endpoints and prefixes them with the API version.
"""

from fastapi import APIRouter

from app.api.endpoints import orders, products, users
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# Add authentication endpoints
auth_router = APIRouter()
auth_router.include_router(users.router, prefix="/auth", tags=["auth"])
