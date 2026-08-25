import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "RecoverIQ"),
    description="AI Revenue Recovery Orchestrator",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": os.getenv("APP_NAME"),
        "environment": os.getenv("APP_ENV"),
        "status": "running",
        "message": "AI Revenue Recovery Orchestrator",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }