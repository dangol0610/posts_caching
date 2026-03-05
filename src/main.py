from fastapi import FastAPI
from src.routers.api_router import router as api_router

app = FastAPI(
    title="Posts Service",
    description="Сервис создания и получения постов",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "ok"}
