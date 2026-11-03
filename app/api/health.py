from fastapi import APIRouter, status

router = APIRouter(tags=["Health & Telemetry"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Returns server operational status, environment, and agent readiness.
    """
    return {
        "status": "healthy",
        "service": "OmniAgent AI Platform Backend",
        "agents": {
            "supervisor": "ready",
            "text": "online",
            "audio": "pending",
            "image": "pending",
            "video": "pending"
        }
    }

