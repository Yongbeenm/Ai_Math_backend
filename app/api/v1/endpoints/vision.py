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
    
    # Extract exercise structure if not already present
    from app.core.khmer.exercise_parser import parse_exercise
    exercise_meta = vision_result.exercise_metadata
    if not exercise_meta:
        parsed_ex = parse_exercise(vision_result.detected_text)
        exercise_meta = {
            "exercise_title": parsed_ex.exercise_title,
            "instruction": parsed_ex.instruction,
            "primary_expression": parsed_ex.primary_expression,
            "sub_exercises": [
                {
                    "label": sub.label,
                    "raw_text": sub.raw_text,
                    "expression": sub.expression,
                    "intent": sub.intent,
                }
                for sub in parsed_ex.sub_exercises
            ],
        }

    # Solve question: prioritize primary_expression if available, fallback to full text
    text_to_solve = exercise_meta.get("primary_expression") or vision_result.detected_text

    try:
        try:
            solve_data = process_question(text_to_solve)
        except MathProcessingError:
            # Fallback to full detected text if primary expression alone had issues
            if text_to_solve != vision_result.detected_text:
                solve_data = process_question(vision_result.detected_text)
            else:
                raise
        
        # Add OCR & Exercise metadata to response
        solve_data_dict = solve_data.model_dump()
        solve_data_dict["ocr_detected_text"] = vision_result.detected_text
        solve_data_dict["ocr_confidence"] = vision_result.confidence
        solve_data_dict["exercise_title"] = exercise_meta.get("exercise_title")
        solve_data_dict["instruction"] = exercise_meta.get("instruction")
        solve_data_dict["sub_exercises"] = exercise_meta.get("sub_exercises", [])
        solve_data_dict["cleaned_math_expression"] = exercise_meta.get("primary_expression")
        
        return APIResponse(success=True, data=solve_data_dict, error=None)
        
    except MathProcessingError as exc:
        return APIResponse(
            success=False,
            data={
                "ocr_detected_text": vision_result.detected_text,
                "ocr_confidence": vision_result.confidence,
                "exercise_title": exercise_meta.get("exercise_title"),
                "instruction": exercise_meta.get("instruction"),
                "sub_exercises": exercise_meta.get("sub_exercises", []),
                "cleaned_math_expression": exercise_meta.get("primary_expression"),
            },
            error=f"OCR detected '{vision_result.detected_text}' but failed to solve: {str(exc)}"
        )
