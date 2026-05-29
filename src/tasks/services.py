from typing import Optional

from fastapi_mail.errors import ConnectionErrors

from src.services import servicemethod
from src.services import BaseService
from src.tasks.models import TaskStatus, Task
from src.tasks.repositories import TaskRepository


from src.mail import send_task_notification

class TaskService(BaseService):
    def __init__(self, repository: TaskRepository):
        super().__init__(repository)

    async def all(self, offset: int = 0, limit: int = 10, status: Optional[TaskStatus] = None) -> list[Task]:
        return await self.repository.all(offset, limit, status)

    @servicemethod()
    async def complete_task(self, task_id: int) -> Task:
        task = await self.repository.patch(task_id, status=TaskStatus.COMPLETED)
        try:
            await send_task_notification(
                subject=f"Task Completed: {task.title}",
                body=f"Task '{task.title}' (ID: {task.id}) has been marked as completed."
            )
        except ConnectionErrors:
            pass
        
        return task
