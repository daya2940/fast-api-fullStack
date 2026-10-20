from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/api/users", response_model=list[UserResponse])
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


@router.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_user = db.scalar(
        select(models.User).where(
            models.User.email == user_data.email,
            models.User.user_id != user_id,
        )
    )
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user.userName = user_data.userName
    user.description = user_data.description
    user.email = user_data.email
    user.image_file = user_data.image_file
    user.image_path = f"/media/{user_data.image_file}" if user_data.image_file else None
    db.commit()
    db.refresh(user)
    return user


@router.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user_partial(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "email" in update_data:
        existing_user = db.scalar(
            select(models.User).where(
                models.User.email == update_data["email"],
                models.User.user_id != user_id,
            )
        )
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if "image_file" in update_data:
        image_file = update_data["image_file"]
        update_data["image_path"] = f"/media/{image_file}" if image_file else None

    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    has_posts = db.scalar(
        select(models.Post.post_id).where(models.Post.user_id == user_id).limit(1)
    )
    if has_posts is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a user who still has posts",
        )

    db.delete(user)
    db.commit()