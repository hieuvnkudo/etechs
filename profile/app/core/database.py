from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings


# Tạo async engine với SQLite
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


# Tạo async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency để lấy async session
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


# Hàm để tạo tất cả các bảng
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Hàm để đóng engine khi shutdown
async def close_db():
    await engine.dispose()

