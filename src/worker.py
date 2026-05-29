import asyncio
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import delete
from datetime import datetime, timezone
from src.config import settings
from src.database import engine
from src.tasks.models import Task, TaskStatus

from sqlalchemy import delete, select
from src.mail import send_task_notification

celery_broker_url = f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db.cache}"

celery_app = Celery("worker", broker=celery_broker_url, backend=celery_broker_url)

@celery_app.task
def delete_overdue_tasks():
    async def _process():
        async with engine.begin() as conn:
            now = datetime.now(timezone.utc)
            
            # Find overdue tasks
            select_stmt = select(Task).where(
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED
            )
            result = await conn.execute(select_stmt)
            overdue_tasks = result.scalars().all()
            
            if overdue_tasks:
                task_list = "\n".join([f"- {t.title} (ID: {t.id}, Due: {t.due_date})" for t in overdue_tasks])
                await send_task_notification(
                    subject=f"Overdue Tasks Notification",
                    body=f"The following tasks are overdue and will be deleted:\n{task_list}"
                )
                
                # Delete overdue tasks
                delete_stmt = delete(Task).where(
                    Task.id.in_([t.id for t in overdue_tasks])
                )
                await conn.execute(delete_stmt)
    
    asyncio.run(_process())

celery_app.conf.beat_schedule = {
    "delete-overdue-tasks-every-hour": {
        "task": "src.worker.delete_overdue_tasks",
        "schedule": crontab(minute=0),
    },
}
