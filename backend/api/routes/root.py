from fastapi import APIRouter

from backend.api.config import settings

router = APIRouter(
    prefix="/api",
    tags=["System"],
)


@router.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "running",
        "message": "AI Revenue Recovery Orchestrator",
    }