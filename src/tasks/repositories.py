from typing import Optional

from sqlalchemy import select

from src.repositories import BaseRepository
from src.tasks.models import TaskStatus, Task


class TaskRepository(BaseRepository):
    def __init__(self, session, model):
        super().__init__(session, model)

    async def all(self, offset: int = 0, limit: int = 10, status: Optional[TaskStatus] = None) -> list[Task]:
        query = select(self.model).offset(offset).limit(limit)

        if status:
            query = query.where(self.model.status == status)

        result = await self.session.execute(query)
        return result.scalars().all()
