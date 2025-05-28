"""
CRUD operations for the Product model.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.models import Category, Product, product_category
from app.schemas.schemas import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """CRUD operations for Product model."""
    
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ProductCreate, owner_id: int
    ) -> Product:
        """
        Create a new product with owner.
        
        Args:
            db: Database session
            obj_in: Product data
            owner_id: User ID of the owner
            
        Returns:
            Product: Created product
        """
        obj_in_data = obj_in.dict(exclude={"category_ids"})
        db_obj = Product(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Add categories if provided
        if obj_in.category_ids:
            await self._add_categories(db, db_obj, obj_in.category_ids)
            
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get multiple products by owner.
        
        Args:
            db: Database session
            owner_id: User ID of the owner
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Product]: List of products
        """
        result = await db.execute(
            select(self.model)
            .filter(Product.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Product,
        obj_in: ProductUpdate
    ) -> Product:
        """
        Update a product.
        
        Args:
            db: Database session
            db_obj: Product to update
            obj_in: Product data to update
            
        Returns:
            Product: Updated product
        """
        update_data = obj_in.dict(exclude_unset=True, exclude={"category_ids"})
        
        # Update regular fields
        for field in update_data:
            setattr(db_obj, field, update_data[field])
            
        # TODO: Handle categories update in async way
        # For now, just update basic fields
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def _add_categories(self, db: AsyncSession, product: Product, category_ids: List[int]) -> None:
        """
        Add categories to a product.
        
        Args:
            db: Database session
            product: Product object
            category_ids: List of category IDs
        """
        # TODO: Implement async category addition
        # For now, this is a placeholder
        pass
        
    async def get_by_sku(self, db: AsyncSession, *, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            db: Database session
            sku: Product SKU
            
        Returns:
            Optional[Product]: Product or None if not found
        """
        result = await db.execute(select(Product).filter(Product.sku == sku))
        return result.scalar_one_or_none()
        
    async def search(
        self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Search products by name or description.
        
        Args:
            db: Database session
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Product]: List of matching products
        """
        search_query = f"%{query}%"
        result = await db.execute(
            select(self.model)
            .filter(
                (Product.name.ilike(search_query)) | 
                (Product.description.ilike(search_query))
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


product = CRUDProduct(Product)
