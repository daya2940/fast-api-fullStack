from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()


@router.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    statement = select(models.Post).options(selectinload(models.Post.author))
    result = await db.scalars(statement)
    return result.all()


@router.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = await db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = await db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != post_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")     

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

@router.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = await db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    update_data=post_data.model_dump(exclude_unset=True) # model_dump(exclude_unset=True) will return a dictionary of only the fields that were provided in the request body, excluding any fields that were not set. This allows for partial updates of the post object, where only the provided fields are updated while the rest remain unchanged.
    for key, value in update_data.items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

@router.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    post = await db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await db.delete(post)
    await db.commit()
    


@router.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    author = await db.get(models.User, post.user_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author=author,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post