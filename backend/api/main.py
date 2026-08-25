from fastapi import FastAPI

from backend.api.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Revenue Recovery Orchestrator",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "running",
        "message": "AI Revenue Recovery Orchestrator",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }