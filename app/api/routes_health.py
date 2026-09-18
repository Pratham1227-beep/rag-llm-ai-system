import datetime
from fastapi import APIRouter
from app.models.schemas import HealthCheckResponse
from app.config import settings
from app.services.vectordb import VectorDBService
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthCheckResponse)
def health_check():
    vdb_status = VectorDBService.get_status()
    ollama_ok, ollama_msg = OllamaClient.check_health()
    overall_status = "healthy" if ollama_ok else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        vector_db_status=vdb_status,
        ollama_status=ollama_msg,
        ollama_model=settings.OLLAMA_MODEL,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
