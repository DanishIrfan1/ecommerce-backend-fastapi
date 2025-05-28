# Import all the models here so that Alembic can auto-discover them
from app.db.session import Base
from app.models.models import User, Address, Product, Category, product_category, Order, OrderItem
