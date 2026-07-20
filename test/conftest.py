import pytest
from typing import AsyncGenerator, Dict
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

from app.models import Base
from app.main import app
from app.database import get_session
from app.cache import redis_client

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL не задан в переменных окружения!")

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def cleanup_after_all_tests():
    yield
    await redis_client.aclose()
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient) -> Dict:
    response = await client.post("/register", json={
        "email": "vasya@artem.com",
        "password": "jentelmen"
    })

    response: Response = await client.post("/login", data={
        "username": "vasya@artem.com",
        "password": "jentelmen"
    })

    print(response.json())
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}