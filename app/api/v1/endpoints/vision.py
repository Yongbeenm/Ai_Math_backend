from fastapi import APIRouter, File, UploadFile

from app.config import get_settings
from app.core.vision.factory import create_vision_engine
from app.models.schemas import APIResponse
from app.services.math_service import MathProcessingError, process_question

router = APIRouter()
settings = get_settings()

# Create vision engine based on configuration
try:
    _vision_engine = create_vision_engine(settings.vision_provider)
except Exception as e:
    # Fall back to stub if provider initialization fails
    from app.core.vision.stub import NotImplementedVisionEngine
    _vision_engine = NotImplementedVisionEngine()
    print(f"Warning: Failed to initialize vision provider '{settings.vision_provider}': {e}")
    print("Falling back to stub provider.")


@router.post("/math/vision", response_model=APIResponse, tags=["math"])
async def vision_solve(image: UploadFile = File(...)) -> APIResponse:
    """
    Math Vision endpoint: photo -> OCR -> solve -> step-by-step solution.
    
    Flow:
    1. Receive image from camera
    2. Use configured OCR provider to detect math text
    3. Feed detected text through the same math pipeline as /math/solve
    4. Return solved answer with steps
    
    Configuration:
    - Set VISION_PROVIDER environment variable to choose OCR provider
    - See docs/VISION_OCR_SETUP.md for setup instructions
    """
    # Read uploaded image
    image_bytes = await image.read()
    
    # Detect text using OCR
    vision_result = _vision_engine.detect(image_bytes)
    
    # If OCR failed or returned no text
    if vision_result.error_message or not vision_result.detected_text:
        return APIResponse(
            success=False,
            data=None,
            error=vision_result.error_message or "No mathematical text detected in image"
        )
    
    # Process the detected text through the math pipeline
    try:
        solve_data = process_question(vision_result.detected_text)
        
        # Add OCR metadata to response
        solve_data_dict = solve_data.model_dump()
        solve_data_dict["ocr_detected_text"] = vision_result.detected_text
        solve_data_dict["ocr_confidence"] = vision_result.confidence
        
        return APIResponse(success=True, data=solve_data_dict, error=None)
        
    except MathProcessingError as exc:
        return APIResponse(
            success=False,
            data={
                "ocr_detected_text": vision_result.detected_text,
                "ocr_confidence": vision_result.confidence
            },
            error=f"OCR detected '{vision_result.detected_text}' but failed to solve: {str(exc)}"
        )
