"""
Vision providers for mathematical OCR.

DEPRECATED: This module has been moved to app/ocr/
Please update imports to use app.ocr instead.
Backward compatibility maintained for now.
"""

import warnings

# Backward compatibility - import from new location
from app.ocr.extraction.base import BaseVisionEngine, VisionResult
from app.ocr.extraction.factory import create_vision_engine, list_available_providers

# Warn about deprecated import
warnings.warn(
    "app.core.vision is deprecated. Please use app.ocr instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["BaseVisionEngine", "VisionResult", "create_vision_engine", "list_available_providers"]
