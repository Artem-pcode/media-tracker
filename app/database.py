from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:temafps228@localhost:5432/media_tracker"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

from typing import AsyncGenerator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as s:
        yield s