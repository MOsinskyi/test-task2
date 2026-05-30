import functools

from fastapi import HTTPException, status

from src.database import Base
from src.repositories import BaseRepository, InstanceNotFound


def servicemethod():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except InstanceNotFound as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        return wrapped
    return wrapper


class BaseService:
    def __init__(self, repository: BaseRepository) -> None:
        self.__repository = repository

    @property
    def repository(self) -> BaseRepository:
        return self.__repository

    async def create(self, **kwargs) -> Base:
        return await self.repository.create(**kwargs)

    @servicemethod()
    async def get(self, id_: int) -> Base | None:
        return await self.repository.get(id_)

    @servicemethod()
    async def patch(self, id_: int, **kwargs) -> Base:
        return await self.repository.patch(id_, **kwargs)

    @servicemethod()
    async def delete(self, id_: int) -> None:
        return await self.repository.delete(id_)

    @servicemethod()
    async def all(self, offset: int = 0, limit: int = 10) -> list[Base]:
        return await self.repository.all(offset, limit)

