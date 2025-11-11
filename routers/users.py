from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from auth import create_access_token, get_current_user, get_db
from models import User
from schemas import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
def register_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    db_user = crud.get_user_by_email(db, payload.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created = crud.create_user(db, payload)
    return {
        "success": True,
        "data": {"user_id": created.id},
        "message": "created",
        "meta": {},
    }


@router.post("/login")
def login(form_data: UserLogin, db: Annotated[Session, Depends(get_db)]):
    user = crud.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        subject=user.email,
        user_id=str(user.id),
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/", response_model=list[UserOut])
def list_users(db: Annotated[Session, Depends(get_db)]):
    return crud.get_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieve a single user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    updates: UserCreate,  # ✅ Accept any dict of fields
    db: Annotated[Session, Depends(get_db)],
):
    """Dynamically update only the provided fields of a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    updated_user = crud.update_user(db, user_id, updates)
    return updated_user
