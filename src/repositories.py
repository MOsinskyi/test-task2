from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Base


class InstanceNotFound(Exception):
    pass


class BaseRepository:
    def __init__(self, session: AsyncSession, model: type[Base]):
        self.__session = session
        self.__model = model

    @property
    def session(self):
        return self.__session

    @property
    def model(self):
        return self.__model

    async def all(self, offset: int = 0, limit: int = 10) -> list[Base]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> Base:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, id_: int) -> Base | None:
        instance = await self.session.get(self.model, id_)

        if not instance:
            raise InstanceNotFound(f"{self.model.__name__} not found")

        return instance

    async def patch(self, id_: int, **kwargs) -> Base:
        instance = await self.get(id_)

        for key, value in kwargs.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id_: int) -> None:
        instance = await self.get(id_)

        await self.session.delete(instance)
        await self.session.commit()
        return None

