from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config.settings import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name, version=settings.app_version)
