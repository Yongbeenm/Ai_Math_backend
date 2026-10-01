"""
OCR Layer - Optical Character Recognition for mathematical content.

This module handles:
- Image preprocessing (contrast, noise reduction, binarization)
- OCR extraction (multiple engines: Kiri, Gemini, Google Vision, Mathpix, etc.)
- OCR normalization (postprocessing and error correction)

Refactored from app/core/vision/ for better modularity.
"""

# Backward compatibility - import from new locations
from app.ocr.extraction.base import BaseVisionEngine, VisionResult
from app.ocr.extraction.factory import create_vision_engine, list_available_providers
from app.ocr.preprocessing.image_preprocessor import PreprocessMode, preprocess_image

__all__ = [
    "BaseVisionEngine",
    "VisionResult",
    "create_vision_engine",
    "list_available_providers",
    "preprocess_image",
    "PreprocessMode",
]
