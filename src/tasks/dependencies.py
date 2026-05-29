from typing import Annotated

from fastapi import Depends

from src.tasks.models import Task
from src.tasks.repositories import TaskRepository
from src.database import SessionDep
from src.tasks.services import TaskService


async def get_task_repository(session: SessionDep) -> TaskRepository:
    return TaskRepository(session, Task)


async def get_task_service(repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repository)


ServiceDep = Annotated[TaskService, Depends(get_task_service)]
