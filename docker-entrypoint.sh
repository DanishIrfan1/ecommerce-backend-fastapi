#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
wait-for-it postgres:5432 --timeout=30 --strict -- echo "PostgreSQL is ready"

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Create superuser if it doesn't exist
echo "Creating superuser..."
python scripts/create_superuser.py

# Start the application
echo "Starting FastAPI application..."
exec "$@"
