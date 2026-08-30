from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.config import settings
from backend.api.routes.health import router as health_router
from backend.api.routes.root import router as root_router
from backend.api.routes.webhooks import router as webhooks_router
from backend.api.routes.analytics import router as analytics_router
from backend.api.routes.payments import router as payments_router


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Revenue Recovery Orchestrator",
    version="0.1.0",
)


# ------------------------------------------------------------
# CORS
# Allows the React frontend running on port 5173
# to communicate with the FastAPI backend on port 8000.
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# API ROUTES
# ------------------------------------------------------------

app.include_router(root_router)
app.include_router(health_router)
app.include_router(webhooks_router)
app.include_router(analytics_router)
app.include_router(payments_router)