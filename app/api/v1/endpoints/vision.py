"""
Math Vision endpoint: Photo -> OCR -> Mathematical extraction -> Solver -> Steps.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.config import get_settings
from app.core.exceptions import MathProcessingError, VisionProcessingError
from app.core.logging import get_logger
from app.core.vision.base import BaseVisionEngine
from app.core.vision.factory import create_vision_engine
from app.core.vision.stub import NotImplementedVisionEngine
from app.models.schemas import APIResponse
from app.services.math_service import MathService, get_math_service
from app.services.vision_service import VisionService

router = APIRouter()
logger = get_logger("app.api.vision")
settings = get_settings()

# Module-level default vision engine (maintained for backwards compatibility with tests)
try:
    _vision_engine: BaseVisionEngine = create_vision_engine(settings.vision_provider)
except Exception as exc:
    logger.warning(
        f"Failed to initialize vision provider '{settings.vision_provider}': {exc}. "
        "Falling back to stub provider."
    )
    _vision_engine = NotImplementedVisionEngine()


def get_vision_engine() -> BaseVisionEngine:
    """Dependency provider for the vision OCR engine, defaulting to _vision_engine."""
    return _vision_engine


@router.post("/math/vision", response_model=APIResponse, tags=["vision"])
async def vision_solve(
    image: UploadFile = File(...),
    vision_engine: BaseVisionEngine = Depends(get_vision_engine),
    math_service: MathService = Depends(get_math_service),
) -> APIResponse:
    """
    Math Vision endpoint: photo -> OCR -> solve -> step-by-step solution.
    """
    image_bytes = await image.read()
    service = VisionService(vision_engine=vision_engine, math_service=math_service)

    try:
        data = service.process_image(image_bytes)
        return APIResponse(success=True, data=data, error=None)
    except VisionProcessingError as exc:
        return APIResponse(success=False, data=None, error=exc.message)
    except MathProcessingError as exc:
        return APIResponse(success=False, data=exc.details, error=exc.message)
