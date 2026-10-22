from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas import UserCreate, UserPrivate, UserPublic, UserUpdate, PostCreate, PostResponse, PostUpdate, Token
from datetime import timedelta
from auth import create_access_token,hash_password, verify_password,verify_access_token
from config import settings
from auth import oauth2_scheme

router = APIRouter()


@router.get("/api/users", response_model=list[UserPublic])
async def read_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(models.User))
    return result.all()


@router.get("/api/users/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/api/users", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await db.scalar(select(models.User).where(func.lower(models.User.email) == func.lower(user.email)))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = models.User(
        userName=user.userName,
        description=user.description,
        email=user.email,
        image_file=user.image_file,
        image_path=f"/media/{user.image_file}" if user.image_file else None,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# token checking route
@router.post("/api/users/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.scalar(
        select(models.User).where(
            func.lower(models.User.email) == func.lower(form_data.username)
        )
    )
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#to check the current user based on the token provided in the Authorization header
@router.get('/me',response_model=UserPrivate)
async def get_current_user( token:Annotated[str, Depends(oauth2_scheme)], 
                           db: Annotated[AsyncSession, Depends(get_db)], 
                           ):
    user_id=verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user = await db.get(models.User, int(user_id['sub']))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.put("/api/users/{user_id}", response_model=UserPrivate)
async def update_user(user_id: int, user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_user = await db.scalar(
        select(models.User).where(
            func.lower(models.User.email) == func.lower(user_data.email),
            models.User.user_id != user_id,
        )
    )
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user.userName = user_data.userName
    user.description = user_data.description
    user.email = user_data.email.lower()
    user.password_hash = hash_password(user_data.password)
    user.image_file = user_data.image_file
    user.image_path = f"/media/{user_data.image_file}" if user_data.image_file else None
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/api/users/{user_id}", response_model=UserPrivate)
async def update_user_partial(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "email" in update_data:
        existing_user = await db.scalar(
            select(models.User).where(
                func.lower(models.User.email) == func.lower(update_data["email"]),
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
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    user = await db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    has_posts = await db.scalar(
        select(models.Post.post_id).where(models.Post.user_id == user_id).limit(1)
    )
    if has_posts is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a user who still has posts",
        )

    await db.delete(user)
    await db.commit()