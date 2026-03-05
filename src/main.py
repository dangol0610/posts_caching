from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.routers.api_router import router as api_router
from src.utils.database import engine
from src.utils.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.close()
    await engine.dispose()


app = FastAPI(
    title="Posts Service",
    description="Сервис создания и получения постов",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "ok"}
