"""
CRUD operations for the Order model.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.models import Order, OrderItem, Product
from app.schemas.schemas import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """CRUD operations for Order model."""
    
    def create_with_items(
        self, db: Session, *, obj_in: OrderCreate, customer_id: int
    ) -> Order:
        """
        Create a new order with items.
        
        Args:
            db: Database session
            obj_in: Order data
            customer_id: User ID of the customer
            
        Returns:
            Order: Created order
        """
        # Calculate total amount and collect order items
        total_amount = 0.0
        order_items = []
        
        for item in obj_in.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ValueError(f"Product with id {item.product_id} not found")
            
            if product.inventory < item.quantity:
                raise ValueError(f"Insufficient inventory for product {product.name}")
            
            unit_price = item.unit_price if item.unit_price else product.price
            item_total = unit_price * item.quantity
            total_amount += item_total
            
            # Prepare order item
            order_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": unit_price
            })
            
            # Update inventory
            product.inventory -= item.quantity
            
        # Create the order
        order_data = obj_in.dict(exclude={"items"})
        db_obj = Order(**order_data, customer_id=customer_id, total_amount=total_amount)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create order items
        for item_data in order_items:
            db_order_item = OrderItem(order_id=db_obj.id, **item_data)
            db.add(db_order_item)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_multi_by_customer(
        self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get multiple orders by customer.
        
        Args:
            db: Database session
            customer_id: User ID of the customer
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Order]: List of orders
        """
        return (
            db.query(self.model)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_by_id_with_items(self, db: Session, *, order_id: int) -> Optional[Order]:
        """
        Get an order by ID with all items.
        
        Args:
            db: Database session
            order_id: Order ID
            
        Returns:
            Optional[Order]: Order or None if not found
        """
        return (
            db.query(Order)
            .filter(Order.id == order_id)
            .options(joinedload(Order.items))
            .first()
        )
        
    def cancel_order(self, db: Session, *, db_obj: Order) -> Order:
        """
        Cancel an order and restore inventory.
        
        Args:
            db: Database session
            db_obj: Order to cancel
            
        Returns:
            Order: Updated order
        """
        if db_obj.status != "pending":
            raise ValueError("Only pending orders can be cancelled")
            
        # Restore inventory
        for item in db_obj.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.inventory += item.quantity
                
        db_obj.status = "cancelled"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


order = CRUDOrder(Order)
