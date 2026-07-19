from pydantic import BaseModel, Field
from typing import Literal

class TitleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    content_type: Literal["movie", "series", "anime"]
    year: int = Field(ge=1888, le=2100)

class TitleResponse(BaseModel):
    id: int
    name: str
    type: str
    year: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True