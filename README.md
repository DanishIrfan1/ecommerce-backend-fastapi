# E-commerce Admin API - Back-end Developer Task

A comprehensive RESTful API for an e-commerce admin dashboard built with **Python FastAPI** and **PostgreSQL**, designed to provide detailed insights into sales, revenue, and inventory status while enabling efficient product management.

## Programming Language and Framework

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **API Type**: RESTful API with OpenAPI/Swagger documentation
- **Database**: PostgreSQL

## Core Features

### 1. Sales Status & Analytics
- **Sales Data Retrieval**: Comprehensive endpoints to retrieve, filter, and analyze sales data
- **Revenue Analysis**: Daily, weekly, monthly, and annual revenue breakdowns
- **Period Comparisons**: Compare revenue across different time periods and product categories
- **Advanced Filtering**: Sales data by date range, product, and category
- **Performance Insights**: Sales trends and statistical analysis

### 2. Inventory Management
- **Current Inventory Status**: Real-time inventory levels and stock monitoring
- **Low Stock Alerts**: Automated alerts for products with low inventory
- **Inventory Updates**: Functionality to update inventory levels
- **Change Tracking**: Historical tracking of inventory changes over time
- **Stock Analytics**: Inventory turnover and optimization insights

### 3. Product Management
- **Product Registration**: Complete CRUD operations for new product registration
- **Category Management**: Hierarchical product categorization
- **Product Search**: Advanced search and filtering capabilities
- **Bulk Operations**: Efficient batch product management

### 4. User Management & Security
- **Admin Authentication**: JWT-based authentication system
- **Role-based Access**: Admin and superuser roles
- **User Profile Management**: Admin user profiles and permissions
- **Secure Operations**: Password hashing and token-based security

## Technical Implementation

### Database Design
- **Database**: PostgreSQL with normalized schema
- **ORM**: SQLAlchemy (async) for optimized performance
- **Indexing**: Proper indexing for optimized query performance
- **Relationships**: Well-defined relationships between entities
- **Data Integrity**: Constraints and validations to prevent redundancy

### API Architecture
- **RESTful Standards**: Following REST principles
- **Async Operations**: Full async/await implementation for better performance
- **Input Validation**: Comprehensive Pydantic schema validation
- **Error Handling**: Proper HTTP status codes and error responses
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

### Performance Optimization
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Indexed queries and efficient data retrieval
- **Async Processing**: Non-blocking operations for better scalability
- **Caching Strategy**: Implementation ready for caching solutions

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (recommended)
- PostgreSQL (if running without Docker)

## Installation & Setup

### Option 1: Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd forsit
   ```

2. **Environment Configuration:**
   - Copy and modify the `.env` file if needed
   - The default configuration should work for development

3. **Start with Docker Compose:**
   ```bash
   # Start all services (PostgreSQL, PgAdmin, API)
   docker-compose up -d
   
   # View logs
   docker-compose logs -f api
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PgAdmin: http://localhost:5050 (admin@forsit.com / admin)

### Option 2: Local Development Setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd forsit
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL:**
   ```bash
   # Install PostgreSQL and create database
   sudo apt-get install postgresql postgresql-contrib
   sudo -u postgres createuser --interactive
   sudo -u postgres createdb forsit_db
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Create superuser:**
   ```bash
   python scripts/create_superuser.py
   ```

8. **Start the application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

## API Documentation

Once the application is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

1. **Create a user:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/users/" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
   ```

2. **Get access token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=testpass123"
   ```

3. **Use token for authenticated requests:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## Demo Data

The application includes comprehensive demo data to evaluate API functionality:

- **Sample Products**: Representative product catalog with Amazon & Walmart-style items
- **Sales History**: Historical sales data for revenue analysis and reporting
- **Inventory Records**: Sample inventory levels and stock movements
- **User Accounts**: Demo admin and user accounts for testing
- **Order History**: Sample orders demonstrating the complete e-commerce flow

### Demo Data Population

```bash
# Populate database with demo data
python scripts/populate_demo_data.py

# Create sample admin user
python scripts/create_superuser.py
```

## API Endpoints Overview

The API provides comprehensive endpoints organized by functionality:

### Sales & Analytics Endpoints
- `GET /api/v1/sales/` - Retrieve sales data with filtering options
- `GET /api/v1/sales/revenue/daily` - Daily revenue analysis
- `GET /api/v1/sales/revenue/weekly` - Weekly revenue analysis  
- `GET /api/v1/sales/revenue/monthly` - Monthly revenue analysis
- `GET /api/v1/sales/revenue/annual` - Annual revenue analysis
- `GET /api/v1/sales/compare` - Revenue comparison across periods
- `GET /api/v1/sales/by-category` - Sales analysis by product category
- `GET /api/v1/sales/by-product` - Sales analysis by individual product

### Inventory Management Endpoints
- `GET /api/v1/inventory/` - Current inventory status for all products
- `GET /api/v1/inventory/low-stock` - Products with low stock alerts
- `PUT /api/v1/inventory/{product_id}` - Update inventory levels
- `GET /api/v1/inventory/history/{product_id}` - Inventory change history
- `GET /api/v1/inventory/analytics` - Inventory turnover analytics

### Product Management Endpoints
- `GET /api/v1/products/` - List all products with pagination and filtering
- `POST /api/v1/products/` - Register new product
- `GET /api/v1/products/{product_id}` - Get specific product details
- `PUT /api/v1/products/{product_id}` - Update product information
- `DELETE /api/v1/products/{product_id}` - Remove product from catalog
- `GET /api/v1/products/search` - Advanced product search
- `GET /api/v1/categories/` - Product category management

### Authentication & User Management
- `POST /api/v1/auth/login` - Admin authentication and token generation
- `POST /api/v1/auth/refresh` - Refresh access tokens
- `GET /api/v1/users/me/` - Get current admin user information
- `PUT /api/v1/users/me/` - Update admin user profile
- `GET /api/v1/users/` - List all admin users (superuser only)

### Orders & Transaction History
- `GET /api/v1/orders/` - Retrieve all orders with filtering
- `GET /api/v1/orders/{order_id}` - Get specific order details
- `PUT /api/v1/orders/{order_id}/status` - Update order status
- `GET /api/v1/orders/analytics` - Order analytics and insights

## Database Schema Documentation

The database is designed with a normalized PostgreSQL schema optimized for e-commerce operations:

### Core Tables

#### **users**
- **Purpose**: Admin user accounts and authentication
- **Key Fields**: id, username, email, hashed_password, is_superuser, is_active
- **Relationships**: One-to-many with addresses

#### **products** 
- **Purpose**: Product catalog management
- **Key Fields**: id, name, description, price, sku, inventory_count, is_active
- **Relationships**: Many-to-many with categories, one-to-many with order_items
- **Indexes**: sku (unique), name, price, inventory_count

#### **categories**
- **Purpose**: Product categorization and organization
- **Key Fields**: id, name, description, parent_category_id
- **Relationships**: Many-to-many with products, self-referential for hierarchy
- **Indexes**: name, parent_category_id

#### **orders**
- **Purpose**: Customer order tracking and management
- **Key Fields**: id, user_id, status, total_amount, created_at, updated_at
- **Relationships**: One-to-many with order_items, many-to-one with users
- **Indexes**: user_id, status, created_at, total_amount

#### **order_items**
- **Purpose**: Individual items within customer orders
- **Key Fields**: id, order_id, product_id, quantity, unit_price, total_price
- **Relationships**: Many-to-one with orders and products
- **Indexes**: order_id, product_id

#### **addresses**
- **Purpose**: User shipping and billing addresses
- **Key Fields**: id, user_id, street, city, state, country, postal_code, is_default
- **Relationships**: Many-to-one with users
- **Indexes**: user_id, postal_code

#### **product_categories** (Association Table)
- **Purpose**: Many-to-many relationship between products and categories
- **Key Fields**: product_id, category_id
- **Indexes**: Composite primary key (product_id, category_id)

### Database Relationships

- **Users ↔ Orders**: One-to-many (one user can have multiple orders)
- **Users ↔ Addresses**: One-to-many (one user can have multiple addresses)
- **Orders ↔ Order Items**: One-to-many (one order contains multiple items)
- **Products ↔ Order Items**: One-to-many (one product can be in multiple orders)
- **Products ↔ Categories**: Many-to-many (products can belong to multiple categories)
- **Categories ↔ Categories**: Self-referential (category hierarchy)

### Indexing Strategy

- **Primary Keys**: Clustered indexes on all id fields
- **Foreign Keys**: Indexes on all foreign key relationships
- **Search Fields**: Indexes on frequently searched columns (name, sku, email)
- **Analytics Fields**: Indexes on date/time fields for reporting
- **Composite Indexes**: Multi-column indexes for complex queries

## Project Structure

```
forsit/
├── app/
│   ├── api/
│   │   ├── endpoints/          # API route handlers
│   │   ├── deps.py            # Dependency injection
│   │   └── api.py             # API router setup
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── security.py        # Security utilities
│   ├── crud/
│   │   ├── base.py            # Base CRUD operations
│   │   └── *.py               # Model-specific CRUD
│   ├── db/
│   │   ├── base.py            # Database base imports
│   │   └── session.py         # Database session config
│   ├── models/
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py         # Pydantic schemas
│   └── main.py                # FastAPI app initialization
├── migrations/                 # Alembic migration files
├── scripts/                   # Utility scripts
├── tests/                     # Test files
├── docker-compose.yml         # Docker services
├── Dockerfile                 # API container
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Production Deployment

1. **Environment Variables:**
   - Set strong `SECRET_KEY`
   - Configure production database URL
   - Set `DEBUG=False`
   - Configure CORS origins

2. **Database:**
   - Use managed PostgreSQL service
   - Set up connection pooling
   - Configure backup strategy

3. **Security:**
   - Use HTTPS
   - Set up rate limiting
   - Configure proper CORS
   - Use environment-specific secrets

## Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Write tests for new features
- Use async/await for database operations
- Validate input data with Pydantic schemas
- Handle errors gracefully with proper HTTP status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License.
