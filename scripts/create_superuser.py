"""
Script to create an initial superuser for the application.
Run this after applying migrations.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crud.user import user
from app.schemas.schemas import UserCreate
from app.db.session import AsyncSessionLocal
from app.core.config import settings


async def create_superuser() -> None:
    """
    Create a superuser with the credentials specified in environment variables or use defaults
    """
    async with AsyncSessionLocal() as db:
        existing_user = await user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not existing_user:
            user_in = UserCreate(
                username=settings.FIRST_SUPERUSER_USERNAME,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_active=True
            )
            new_user = await user.create(db, obj_in=user_in)
            print(f"Superuser created: {new_user.username} ({new_user.email})")
        else:
            print(f"Superuser already exists: {existing_user.username} ({existing_user.email})")


if __name__ == "__main__":
    asyncio.run(create_superuser())
