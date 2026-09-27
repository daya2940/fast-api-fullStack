
from fastapi import FastAPI,HTTPException,status,Request,Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from schemas import PostCreate,PostResponse
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

import models
from database import engine,Base,get_db

base = Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


class User(BaseModel):
    id: int
    name: str
    description: str
    age: int
    status: str
    home_address: str


posts = [
    PostResponse(
        id=0,
        title="string",
        content="string",
        published=True,
        date_posted="string"
    ),
    PostResponse(
        id=1,
        title="Alice Johnson",
        content="A software developer who enjoys building web applications.",
        published=True,
        date_posted="string"
    ),
]


@app.get("/", response_model=list[PostResponse], include_in_schema=False) #include_in_schema=True will include this endpoint in the OpenAPI schema
def read_root():
    return {"Hello": "World"}


@app.get("/users", response_model=list[User],include_in_schema=False) #include_in_schema=True will include this endpoint in the OpenAPI schema   
def read_users():
    return posts

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)# url path parameter post_id is used to retrieve a specific post by its ID
def get_post(post_id: int):
    for post in posts:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_post = PostResponse(
        id=len(posts) + 1,
        title=post.title,
        content=post.content,
        published=post.published,
        date_posted="2023-01-01"  # Example date, you can modify this as needed
    )
    posts.append(new_post)
    return new_post