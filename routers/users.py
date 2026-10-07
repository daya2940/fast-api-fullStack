from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import UserCreate, UserResponse

router = APIRouter()


@router.get("/users", response_model=list[UserResponse], include_in_schema=False)
def read_users(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(models.User)).all()


@router.get("/api/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.scalar(select(models.User).where(models.User.email == user.email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = models.User(
        userName=user.userName,
        description=user.description,
        email=user.email,
        image_file=user.image_file,
        image_path=f"/media/{user.image_file}" if user.image_file else None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user