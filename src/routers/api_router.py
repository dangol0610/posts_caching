from fastapi import APIRouter

from src.app.routers import router as post_router

router = APIRouter(prefix="/api")
router.include_router(post_router)
