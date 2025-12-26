from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from .settings import settings

engine = create_async_engine(settings.database_url, echo=True)

async def create_db_and_tables():
    async with engine.begin() as conn:
        from sqlmodel import SQLModel
        from .features.todo.models import Todo  # Import model từ feature mới
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(engine)
    async with async_session as session:
        yield session
