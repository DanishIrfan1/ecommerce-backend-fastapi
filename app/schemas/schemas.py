"""
Pydanfrom datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validatorschemas for data validation and serialization.

This module contains Pydantic models that are used for:
- Input validation
- Response serialization
- OpenAPI documentation
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# Token schemas
class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    """Base schema for user data."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)
    is_superuser: Optional[bool] = False


class UserUpdate(BaseModel):
    """Schema for user update."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for user response."""
    pass


# Address schemas
class AddressBase(BaseModel):
    """Base schema for address data."""
    address_type: str = Field(..., pattern='^(shipping|billing)$')
    street_address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)
    is_default: bool = False


class AddressCreate(AddressBase):
    """Schema for address creation."""
    pass


class AddressUpdate(BaseModel):
    """Schema for address update."""
    address_type: Optional[str] = Field(None, pattern='^(shipping|billing)$')
    street_address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None


class Address(AddressBase):
    """Schema for address response."""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    """Base schema for category data."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for category creation."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for category update."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class Category(CategoryBase):
    """Schema for category response."""
    id: int
    
    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    """Base schema for product data."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    inventory: int = Field(..., ge=0)
    sku: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=255)


class ProductCreate(ProductBase):
    """Schema for product creation."""
    category_ids: Optional[List[int]] = []


class ProductUpdate(BaseModel):
    """Schema for product update."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    inventory: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=255)
    category_ids: Optional[List[int]] = None


class Product(ProductBase):
    """Schema for product response."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: List[Category] = []
    
    class Config:
        from_attributes = True


# OrderItem schemas
class OrderItemBase(BaseModel):
    """Base schema for order item data."""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Optional[float] = None


class OrderItemCreate(OrderItemBase):
    """Schema for order item creation."""
    pass


class OrderItem(OrderItemBase):
    """Schema for order item response."""
    id: int
    unit_price: float
    
    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    """Base schema for order data."""
    shipping_address_id: Optional[int] = None
    billing_address_id: Optional[int] = None


class OrderCreate(OrderBase):
    """Schema for order creation."""
    items: List[OrderItemCreate]

    @field_validator('items')
    @classmethod
    def items_not_empty(cls, v):
        if not len(v):
            raise ValueError('Order must have at least one item')
        return v


class OrderUpdate(BaseModel):
    """Schema for order update."""
    status: Optional[str] = Field(None, pattern='^(pending|processing|shipped|delivered|cancelled)$')
    shipping_address_id: Optional[int] = None
    billing_address_id: Optional[int] = None
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None


class Order(OrderBase):
    """Schema for order response."""
    id: int
    customer_id: int
    order_date: datetime
    total_amount: float
    status: str
    items: List[OrderItem]
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    
    class Config:
        from_attributes = True