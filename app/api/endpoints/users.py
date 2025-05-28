"""
API routes for user authentication and management.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.crud import user
from app.schemas.schemas import Token, User, UserCreate, UserUpdate

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    authenticated_user = user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not user.is_active(authenticated_user):
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            authenticated_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    existing_user = user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )
        
    existing_email = user.get_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
        
    new_user = user.create(db, obj_in=user_in)
    return new_user


@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    # If username is being updated, check that it's not already taken
    if user_in.username and user_in.username != current_user.username:
        existing_user = user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )
    
    # If email is being updated, check that it's not already taken
    if user_in.email and user_in.email != current_user.email:
        existing_email = user.get_by_email(db, email=user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
    
    updated_user = user.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user
