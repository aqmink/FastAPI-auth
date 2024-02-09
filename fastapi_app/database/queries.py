from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, insert
from bcrypt import hashpw, gensalt

from database.models import User
from database.schemas import UserCreate


async def get_users(session: AsyncSession, *args, **kwargs):
    users = await session.execute(select(User).where(**kwargs))
    return users.scalars().all()


async def get_user(session: AsyncSession, username: str):
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalars().first()


async def create_user(user: UserCreate, session: AsyncSession):
    if await get_user(session=session, username=user.username):
        raise ValueError("Username already exists")
    else:
        await session.execute(insert(User).values(
            username=user.username,
            email=user.email,
            password=hashpw(user.password2.encode(), gensalt()),
            is_active=True,
        ))
        await session.commit()
