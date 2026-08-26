from fastapi import FastAPI

from backend.api.config import settings
from backend.api.routes.health import router as health_router
from backend.api.routes.root import router as root_router
from backend.api.routes.webhooks import router as webhooks_router


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Revenue Recovery Orchestrator",
    version="0.1.0",
)


app.include_router(root_router)
app.include_router(health_router)
app.include_router(webhooks_router)