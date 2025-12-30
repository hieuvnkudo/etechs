import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_session
from app.features.todos.model import Todo  # noqa: F401


# Tạo test database engine (in-memory)
@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    # Tạo tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


# Tạo test session
@pytest.fixture(scope="function")
async def test_session(test_engine):
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


# Override get_session dependency
@pytest.fixture(scope="function")
async def override_get_session(test_session):
    async def _get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = _get_session
    yield
    app.dependency_overrides.clear()


# Test client
@pytest.fixture(scope="function")
async def client(override_get_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

