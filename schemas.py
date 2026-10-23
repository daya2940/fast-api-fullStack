from pydantic import BaseModel,ConfigDict,Field,EmailStr
from datetime import datetime

class UserBase(BaseModel):
    userName: str=Field(min_length=1, max_length=100)
    description: str
    email: EmailStr = Field(max_length=120)
    image_file: str | None = Field(default=None)

class UserCreate(UserBase):
    userName: str=Field(min_length=1, max_length=100)
    password: str=Field(min_length=8, max_length=100)
    description: str
    email: EmailStr = Field(max_length=120)
    image_file: str | None = Field(default=None)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    image_file: str | None = Field(default=None)
    image_path: str | None = Field(default=None)

class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=120)

class UserUpdate(UserBase):
    userName: str = Field(default=None, min_length=1, max_length=100)
    description: str = Field(default=None)
    email: EmailStr = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None)

class Token(BaseModel):
    access_token: str
    token_type: str

class PostBase(BaseModel):
    # model_config = ConfigDict(from_attributes=True)
    title: str=Field(min_length=1, max_length=100)
    content: str
    published: bool = Field(default=True)
    # author:int

class PostCreate(PostBase):
    title: str=Field(min_length=1, max_length=100)
    content: str
    published: bool = Field(default=True)

class PostUpdate(PostBase):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None,min_length=1) 
    user_id: int | None = Field(default=None) 

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    post_id: int
    date_posted: datetime
    author: UserPublic
    
