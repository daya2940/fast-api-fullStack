from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate,PaginationPostResponse
from auth import CurrentUser
from fastapi import Query

router = APIRouter()

# This is paginated endpoint for fetching posts. It takes two query parameters: 
# page and size, which determine the page number and the number of posts per page, 
# respectively. The default values are page=1 and size=10, 
# with constraints on the minimum and maximum values for size.
@router.get("/api/posts", response_model=PaginationPostResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    total_posts = await db.scalar(select(func.count(models.Post.post_id)))
    total=total_posts if total_posts is not None else 0
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .offset(skip) #skip the first skip posts and return the next limit posts.
         # This is used for pagination, where skip 
          #is the number of posts to skip and limit is the maximum number of posts to return.
        .limit(limit)
    )
    has_more = (skip + len((await db.scalars(statement)).all())) < total
    # statement = select(models.Post).options(selectinload(models.Post.author))
    # result = await db.scalars(statement)
    # return result.all()
    return PaginationPostResponse(posts=(await db.scalars(statement)).all(), 
                                  total=total, skip=skip, limit=limit, has_more=has_more)


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
async def update_post(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)],current_user: CurrentUser):
    # current user is the user object of the currently authenticated user, 
    # which is obtained from the get_current_user function in auth.py. 
    # This function verifies the access token and retrieves the corresponding user from the database. 
    # The current_user parameter is annotated with CurrentUser, 
    # which is a type alias for models.User that depends on get_current_user. 
    # This means that FastAPI will automatically call get_current_user and inject the returned 
    # user object into the current_user parameter when this endpoint is called.
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = await db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")     

    post.title = post_data.title
    post.content = post_data.content
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

@router.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)], current_user: CurrentUser):
    statement = (
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.post_id == post_id)
    )
    post = await db.scalar(statement)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this post")
    update_data=post_data.model_dump(exclude_unset=True) # model_dump(exclude_unset=True) will return a dictionary of only the fields that were provided in the request body, excluding any fields that were not set. This allows for partial updates of the post object, where only the provided fields are updated while the rest remain unchanged.
    for key, value in update_data.items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

@router.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)], current_user: CurrentUser) -> None:
    post = await db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this post")
    await db.delete(post)
    await db.commit()
    


@router.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)], current_user: CurrentUser):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author=current_user,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post