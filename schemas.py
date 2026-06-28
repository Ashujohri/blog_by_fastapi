from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    image_path: str
    image_file: str | None = None
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)

class PostCreate(PostBase):
    user_id: int  # TEMPORARY

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date_posted: datetime
    author: UserResponse