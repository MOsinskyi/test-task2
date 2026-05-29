from typing import Optional

from fastapi import APIRouter, Query

from src.tasks.models import TaskStatus
from src.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.tasks.dependencies import ServiceDep

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("")
async def create_task(task_in: TaskCreate, service: ServiceDep) -> TaskResponse:
    data = task_in.model_dump()
    return await service.create(**data)

@router.get("")
async def list_tasks(
    service: ServiceDep,
    status: Optional[TaskStatus] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[TaskResponse]:
    return await service.all(offset, limit, status)

@router.get("/{task_id}")
async def get_task(task_id: int, service: ServiceDep) -> TaskResponse:
    return await service.get(task_id)

@router.post("/{task_id}/complete")
async def complete_task(task_id: int, service: ServiceDep) -> TaskResponse:
    return await service.complete_task(task_id)

@router.patch("/{task_id}")
async def update_task(task_id: int, task_in: TaskUpdate, service: ServiceDep) -> TaskResponse:
    return await service.patch(task_id, **task_in.model_dump(exclude_unset=True))

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, service: ServiceDep) -> None:
    return await service.delete(task_id)
