import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app, get_session_maker
from app.core.database import get_session
from app.models import Base

# Setup in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

test_async_session = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="function", autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    # Create the tables before running tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop the tables after running tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override database dependency in FastAPI app
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_get_session_maker():
        return test_async_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_session_maker] = override_get_session_maker

    # We also mock or override database configuration in app.main if needed.
    # Note: app.main has increment_clicks which also needs a session.
    # We will override or handle it. Let's use ASGITransport.
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
