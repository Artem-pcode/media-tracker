from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
import json

from app.auth import get_current_user
from app.database import get_session
from app.models import Title, User
from app.schemas import TitleCreate, TitleResponse
from app.cache import redis_client, invalidate_titles_cache

router = APIRouter(prefix="/titles", tags=["titles"])

@router.get("", response_model=List[TitleResponse])
async def list_titles(
    content_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
) -> List[Dict]:
    cache_key = f"titles:{content_type or 'all'}"

    cache_data = await redis_client.get(cache_key)
    if cache_data is not None:
        return json.loads(cache_data)
    
    query = select(Title)
    if content_type is not None:
        query = query.where(Title.type == content_type)
    result = await session.execute(query)
    titles = result.scalars().all()

    title_list = [TitleResponse.model_validate(t).model_dump() for t in titles]
    await redis_client.set(cache_key, json.dumps(title_list), ex=60)
    return title_list


@router.get("/search", response_model=List[TitleResponse])
async def get_search(
    query_search: str,
    session: AsyncSession = Depends(get_session)
) -> List[Title]:
    query = select(Title).where(Title.name.ilike(f"%{query_search}%"))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{title_id}", response_model=TitleResponse)
async def get_title(
    title_id: int,
    session: AsyncSession = Depends(get_session)
) -> Title:
    title = await session.get(Title, title_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@router.post("", response_model=TitleResponse, status_code=201)
async def create_titles(
    title: TitleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Title:
    new_title = Title(name=title.name, type=title.content_type, year=title.year)
    
    session.add(new_title)
    await session.commit()
    await session.refresh(new_title)

    await invalidate_titles_cache([f"titles:{title.content_type}"])

    return new_title


@router.put("/{title_id}", response_model=TitleResponse)
async def update_title(
    title_id: int,
    title: TitleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Title:
    cur_title = await session.get(Title, title_id)
    if cur_title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    
    orig_type = cur_title.type
    cur_title.name = title.name
    cur_title.type = title.content_type
    cur_title.year = title.year

    await session.commit()
    await session.refresh(cur_title)

    await invalidate_titles_cache([f"titles:{orig_type}", f"titles:{title.content_type}"])

    return cur_title