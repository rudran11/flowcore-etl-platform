from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/health", summary="Liveness Probe")
async def health_check():
    """
    Extremely lightweight endpoint. Returns 200 OK simply if the Uvicorn event loop is unblocked.
    """
    return {"status": "ok"}

@router.get("/ready", summary="Readiness Probe")
async def readiness_check():
    """
    Evaluates if the underlying services are ready to accept tasks.
    In Sub-Sprint 4.1, this is a placeholder that returns ready.
    """
    # Placeholder for checking if PluginManager and EngineRunner are ready
    return {"status": "ready"}
