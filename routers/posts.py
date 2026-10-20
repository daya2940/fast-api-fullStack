from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()


@router.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    statement = select(models.Post).options(selectinload(models.Post.author))
    return db.scalars(statement).all()


@router.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != post_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")     

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    db.commit()
    db.refresh(post)
    return post

@router.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    update_data=post_data.model_dump(exclude_unset=True) # model_dump(exclude_unset=True) will return a dictionary of only the fields that were provided in the request body, excluding any fields that were not set. This allows for partial updates of the post object, where only the provided fields are updated while the rest remain unchanged.
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    


@router.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    author = db.get(models.User, post.user_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author=author,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post