"""
OCR Extraction - Multiple OCR engine implementations.

Supported engines:
- Kiri OCR (custom trained)
- Google Vision API
- Gemini Vision
- Mathpix
- Pix2Tex
- Tesseract
- Ensemble (multiple engines voting)
"""

from app.ocr.extraction.base import BaseVisionEngine, VisionResult
from app.ocr.extraction.factory import create_vision_engine, list_available_providers

__all__ = [
    "BaseVisionEngine",
    "VisionResult",
    "create_vision_engine",
    "list_available_providers",
]
