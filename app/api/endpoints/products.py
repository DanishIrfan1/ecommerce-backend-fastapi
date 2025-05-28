"""
API routes for product management.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import product
from app.models.models import User
from app.schemas.schemas import Product, ProductCreate, ProductUpdate

router = APIRouter()


@router.get("/", response_model=List[Product])
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search products by name or description")
) -> Any:
    """
    Retrieve products.
    
    Optionally filter products by a search term.
    """
    if search:
        products = product.search(db, query=search, skip=skip, limit=limit)
    else:
        products = product.get_multi(db, skip=skip, limit=limit)
    
    return products


@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new product.
    """
    if product_in.sku:
        existing_product = product.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with SKU {product_in.sku} already exists",
            )
    
    return product.create_with_owner(db, obj_in=product_in, owner_id=current_user.id)


@router.get("/me", response_model=List[Product])
def read_products_by_me(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve products owned by current user.
    """
    products = product.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return products


@router.get("/{id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get product by ID.
    """
    product_obj = product.get(db, id=id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product_obj


@router.put("/{id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a product.
    """
    product_obj = product.get(db, id=id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
        
    if product_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this product",
        )
        
    if product_in.sku and product_in.sku != product_obj.sku:
        existing_product = product.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with SKU {product_in.sku} already exists",
            )
    
    return product.update(db, db_obj=product_obj, obj_in=product_in)


@router.delete("/{id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a product.
    """
    product_obj = product.get(db, id=id)
    if not product_obj:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
        
    if product_obj.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this product",
        )
        
    return product.remove(db, id=id)
