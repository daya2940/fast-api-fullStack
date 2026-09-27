from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse

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
        .where(models.Post.id == post_id)
    )
    post = db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


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