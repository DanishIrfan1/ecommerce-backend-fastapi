"""
API routes for order management.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import order
from app.models.models import User
from app.schemas.schemas import Order, OrderCreate, OrderUpdate

router = APIRouter()


@router.get("/", response_model=List[Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve orders for current user.
    """
    orders = order.get_multi_by_customer(
        db, customer_id=current_user.id, skip=skip, limit=limit
    )
    return orders


@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new order.
    """
    try:
        return order.create_with_items(
            db, obj_in=order_in, customer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/{id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get order by ID.
    """
    order_obj = order.get_by_id_with_items(db, order_id=id)
    
    if not order_obj:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
        
    if order_obj.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this order",
        )
        
    return order_obj


@router.put("/{id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an order.
    """
    order_obj = order.get(db, id=id)
    
    if not order_obj:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
        
    if order_obj.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this order",
        )
        
    return order.update(db, db_obj=order_obj, obj_in=order_in)


@router.put("/{id}/cancel", response_model=Order)
def cancel_order(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel an order.
    """
    order_obj = order.get_by_id_with_items(db, order_id=id)
    
    if not order_obj:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
        
    if order_obj.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to cancel this order",
        )
        
    try:
        return order.cancel_order(db, db_obj=order_obj)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
