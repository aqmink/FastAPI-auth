from sqlmodel import SQLModel, select, update, insert, delete

from .connection import AsyncSession


class ORMBase:
    model: SQLModel

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, *filter, **params):
        result = await self.session.execute(
            select(self.model).
            filter(*filter).
            filter_by(**params)
        )
        return result.scalars().first()

    async def get_all(
        self,
        *filter,
        limit: int = 0, 
        offset: int = 50, 
        **params
    ):
        result = await self.session.execute(
            select(self.model).
            filter(*filter).
            filter_by(**params).
            offset(offset).
            limit(limit)
        )
        return result.scalars().all()

    async def create(self, **data):
        await self.session.execute(
            insert(self.model).
            values(**data)
        )
        await self.session.commit()

    async def update(self, *filter, **data):
        await self.session.execute(
            update(self.model).
            filter(*filter).
            values(**data)
        )
        await self.session.commit()

    async def delete(self, *filter, **params):
        await self.session.execute(
            delete(self.model).
            filter(*filter).
            filter_by(**params)
        )
        await self.session.commit()
