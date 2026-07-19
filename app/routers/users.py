from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict

from app.auth import hash_password, verify_password, create_access_token
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.database import get_session

router = APIRouter(tags=["/users"])

def send_welcome_email(email: str):
    print(f"Sending mail on {email}")
    import time
    time.sleep(2)
    print(f"Mail has been sent on {email}")


@router.post("/register", response_model=UserResponse, status_code=201)
async def registration(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
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

    background_tasks.add_task(send_welcome_email, new_user.email)

    return new_user


@router.post("/login")
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