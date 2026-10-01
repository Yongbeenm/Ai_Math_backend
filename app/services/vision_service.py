"""
Vision service orchestrating OCR detection, exercise parsing, and mathematical solving.
"""

from __future__ import annotations

from typing import Any

from app.core.exceptions import MathProcessingError, VisionProcessingError
from app.core.khmer.exercise_parser import parse_exercise
from app.core.logging import get_logger
from app.core.vision.base import BaseVisionEngine, VisionResult
from app.services.math_service import MathService

logger = get_logger("app.services.vision")


class VisionService:
    """Service encapsulating the image OCR to math solution workflow."""

    def __init__(
        self,
        vision_engine: BaseVisionEngine,
        math_service: MathService | None = None,
    ) -> None:
        self.vision_engine = vision_engine
        self.math_service = math_service or MathService()

    def process_image(self, image_bytes: bytes) -> dict[str, Any]:
        """
        Executes OCR detection, parses exercise structure, and solves the detected math.
        """
        vision_result: VisionResult = self.vision_engine.detect(image_bytes)

        if vision_result.error_message or not vision_result.detected_text:
            err = vision_result.error_message or "No mathematical text detected in image"
            raise VisionProcessingError(err)

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

        text_to_solve = exercise_meta.get("primary_expression") or vision_result.detected_text

        try:
            try:
                solve_data = self.math_service.process_question(text_to_solve)
            except MathProcessingError:
                if text_to_solve != vision_result.detected_text:
                    solve_data = self.math_service.process_question(vision_result.detected_text)
                else:
                    raise

            solve_data_dict = solve_data.model_dump()
            solve_data_dict["ocr_detected_text"] = vision_result.detected_text
            solve_data_dict["ocr_confidence"] = vision_result.confidence
            solve_data_dict["exercise_title"] = exercise_meta.get("exercise_title")
            solve_data_dict["instruction"] = exercise_meta.get("instruction")
            solve_data_dict["sub_exercises"] = exercise_meta.get("sub_exercises", [])
            solve_data_dict["cleaned_math_expression"] = exercise_meta.get("primary_expression")

            return solve_data_dict

        except MathProcessingError as exc:
            partial_data = {
                "ocr_detected_text": vision_result.detected_text,
                "ocr_confidence": vision_result.confidence,
                "exercise_title": exercise_meta.get("exercise_title"),
                "instruction": exercise_meta.get("instruction"),
                "sub_exercises": exercise_meta.get("sub_exercises", []),
                "cleaned_math_expression": exercise_meta.get("primary_expression"),
            }
            raise MathProcessingError(
                message=f"OCR detected '{vision_result.detected_text}' but failed to solve: {exc}",
                details=partial_data,
            ) from exc
