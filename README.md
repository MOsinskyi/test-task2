# To-Do List API

## Features

- **CRUD Operations**: Create, read, update, and delete tasks.
- **Task Completion**: Dedicated endpoint to mark tasks as completed.
- **Filtering & Pagination**: List tasks with status filtering and configurable limits/offsets.
- **Background Tasks**: Automatic deletion of overdue tasks via Celery Beat.
- **Email Notifications**: Alerts when a task is completed or when overdue tasks are detected/deleted.
- **Rate Limiting**: Throttling for API protection using `fastapi-limiter`.
- **Dockerized**: Fully containerized environment with Docker Compose.

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.14+
- Poetry

### Option 1: Running with Docker (Recommended)

1. **Configure Environment**:
   ```bash
   cp .env.template .env
   ```

2. **Start Services**:
   ```bash
   docker compose up --build -d
   ```
3. **Database Migrations**:
   ```bash
   docker exec -it todo_app alembic upgrade head    
   ```

### Option 2: Running Locally

1. **Install Dependencies**:
   ```bash
   poetry install
   ```

2. **Setup Infrastructure**:
   Ensure you have PostgreSQL and Redis running locally. Update `.env` accordingly.

3. **Apply Migrations**:
   ```bash
   PYTHONPATH=. poetry run alembic upgrade head
   ```

4. **Run Application**:
   ```bash
   PYTHONPATH=. poetry run src/main.py
   ```

5. **Run Celery**:
   ```bash
   PYTHONPATH=. poetry run celery -A src.worker.celery_app worker --loglevel=info
   PYTHONPATH=. poetry run celery -A src.worker.celery_app beat --loglevel=info
   ```

---

## API Documentation

Once the app is running, visit: [http://localhost:8000/docs](http://localhost:8000/docs)

### Primary Endpoints

| Method   | Endpoint               | Description                                     |
|----------|------------------------|-------------------------------------------------|
| `POST`   | `/tasks`               | Create a new task                               |
| `GET`    | `/tasks`               | List tasks (query: `status`, `limit`, `offset`) |
| `GET`    | `/tasks/{id}`          | Get task details                                |
| `PATCH`  | `/tasks/{id}`          | Update task fields                              |
| `POST`   | `/tasks/{id}/complete` | Mark task as completed (triggers email)         |
| `DELETE` | `/tasks/{id}`          | Delete a task                                   |

---

## Background Tasks

The Celery Beat scheduler is configured to run `delete_overdue_tasks` every hour.

- It checks for tasks where `due_date < current_time` and status is not `COMPLETED`.
- It sends an email summary of overdue tasks.
- it deletes the overdue tasks from the database.

---

## Testing

Run the test suite using `pytest`. Testing is performed against the real database but uses `NullPool` for clean
isolation.

```bash
TESTING=1 PYTHONPATH=. poetry run pytest
```
