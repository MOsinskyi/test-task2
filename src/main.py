import os

import uvicorn
from fastapi import FastAPI
from fastapi_limiter.middleware import RateLimiterMiddleware
from pyrate_limiter import Duration, Limiter, Rate

from src.config import settings
from src.tasks.routers import router

app = FastAPI(title="To-Do List API")

if not os.getenv("TESTING"):
    app.add_middleware(
        RateLimiterMiddleware,
        limiter=Limiter(Rate(settings.throttling.limit, Duration.SECOND * settings.throttling.seconds)),
    )

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Test task 2"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app.host, port=settings.app.port)
