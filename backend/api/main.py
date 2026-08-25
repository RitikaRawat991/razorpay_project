from fastapi import FastAPI

app = FastAPI(
    title="RecoverIQ",
    description="AI Revenue Recovery Orchestrator",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": "RecoverIQ",
        "status": "running",
        "message": "AI Revenue Recovery Orchestrator",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }