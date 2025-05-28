"""
Consolidation of all CRUD operations.

This module exports all CRUD operations for easy importing elsewhere.
"""

from app.crud.base import CRUDBase
from app.crud.order import order
from app.crud.product import product
from app.crud.user import user

# For convenience, export all CRUD instances
__all__ = ["user", "product", "order"]
