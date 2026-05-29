import asyncio
from datetime import datetime, timezone

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select

from src.config import settings
from src.database import AsyncSessionLocal
from src.mail import send_task_notification
from src.tasks.models import Task, TaskStatus

celery_broker_url = f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db.cache}"

celery_app = Celery("worker", broker=celery_broker_url, backend=celery_broker_url)

@celery_app.task
def delete_overdue_tasks():
    async def _process():
        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)

            select_stmt = select(Task).where(
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED
            )
            result = await session.execute(select_stmt)
            overdue_tasks = result.scalars().all()
            
            if overdue_tasks:
                task_list = "\n".join([f"- {t.title} (ID: {t.id}, Due: {t.due_date})" for t in overdue_tasks])
                await send_task_notification(
                    subject=f"Overdue Tasks Notification",
                    body=f"The following tasks are overdue and will be deleted:\n{task_list}"
                )

                for task in overdue_tasks:
                    await session.delete(task)
                
                await session.commit()
    
    asyncio.run(_process())

celery_app.conf.beat_schedule = {
    "delete-overdue-tasks-every-hour": {
        "task": "src.worker.delete_overdue_tasks",
        "schedule": crontab(minute=0),
    },
}
