from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session
from models import Title, User
from auth import get_current_user

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

app = FastAPI(title="MediaTracker API")

@app.get("/")
def root() -> Dict:
    return {"message": "MediaTracker API is running"}


@app.get("/titles", response_model=List[TitleResponse])
async def list_titles(
    content_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
) -> List[Title]:
    query = select(Title)
    if content_type is not None:
        query = query.where(Title.type == content_type)
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/titles/search", response_model=List[TitleResponse])
async def get_search(
    query_search: str,
    session: AsyncSession = Depends(get_session)
) -> List[Title]:
    query = select(Title).where(Title.name.ilike(f"%{query_search}%"))
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/titles/{title_id}", response_model=TitleResponse)
async def get_title(
    title_id: int,
    session: AsyncSession = Depends(get_session)
) -> Title:
    title = await session.get(Title, title_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@app.post("/titles", response_model=TitleResponse, status_code=201)
async def create_titles(
    title: TitleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Title:
    new_title = Title(name=title.name, type=title.content_type, year=title.year)
    session.add(new_title)
    await session.commit()
    await session.refresh(new_title)
    return new_title


@app.put("/titles/{title_id}", response_model=TitleResponse)
async def update_title(
    title_id: int,
    title: TitleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Title:
    cur_title = await session.get(Title, title_id)
    if cur_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    cur_title.name = title.name
    cur_title.type = title.content_type
    cur_title.year = title.year
    await session.commit()
    await session.refresh(cur_title)
    return cur_title

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

from auth import hash_password, verify_password, create_access_token, decode_access_token

@app.post("/register", response_model=UserResponse, status_code=201)
async def registration(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> User:
    existing = await session.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(409, "Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Dict:
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}