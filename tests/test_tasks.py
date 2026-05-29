import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.database import __get_db, Base
from src.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta, timezone

# For tests running on host, override DB host if it's set to docker service name
db_url = settings.postgres.url
if "db" in db_url and "@db" in db_url:
    db_url = db_url.replace("@db", "@localhost")

test_engine = create_async_engine(db_url, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[__get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/tasks", json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_list_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_complete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create
        create_resp = await ac.post("/tasks", json={"title": "To Complete"})
        task_id = create_resp.json()["id"]

        # Complete
        complete_resp = await ac.post(f"/tasks/{task_id}/complete")
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"

@pytest.mark.asyncio
async def test_update_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_resp = await ac.post("/tasks", json={"title": "To Update"})
        task_id = create_resp.json()["id"]

        update_resp = await ac.patch(f"/tasks/{task_id}", json={"status": "completed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "completed"

@pytest.mark.asyncio
async def test_delete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_resp = await ac.post("/tasks", json={"title": "To Delete"})
        task_id = create_resp.json()["id"]

        delete_resp = await ac.delete(f"/tasks/{task_id}")
        assert delete_resp.status_code == 204

        get_resp = await ac.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404
