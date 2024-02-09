from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel

from config import DATABASE_URL

engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async_session = sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
