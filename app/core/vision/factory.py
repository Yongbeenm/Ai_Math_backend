"""
Vision engine factory for easy switching between OCR providers.

This allows you to configure which OCR provider to use via environment
variable without changing code. Useful for:
- Development (use stub or free Tesseract)
- Production (use Mathpix or Google Vision)
- Testing (use stub)
"""
from __future__ import annotations

import os

from app.core.vision.base import MathVisionEngine
from app.core.vision.stub import NotImplementedVisionEngine


def create_vision_engine(provider: str | None = None) -> MathVisionEngine:
    """
    Create a vision engine based on provider name.
    
    Args:
        provider: One of "stub", "tesseract", "mathpix", "google".
                  If None, reads from VISION_PROVIDER environment variable.
                  Defaults to "stub" if not set.
    
    Returns:
        Configured MathVisionEngine instance
    
    Raises:
        ValueError: If provider is unknown
        ImportError: If provider library is not installed
    
    Environment variables:
        VISION_PROVIDER: "stub", "tesseract", "mathpix", or "google"
        
        For Tesseract:
            (none needed - uses local installation)
        
        For Mathpix:
            MATHPIX_APP_ID: Your Mathpix app ID
            MATHPIX_APP_KEY: Your Mathpix app key
        
        For Google Vision:
            GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON
    
    Example:
        >>> engine = create_vision_engine("tesseract")
        >>> result = engine.detect(image_bytes)
    """
    provider = provider or os.getenv("VISION_PROVIDER", "stub")
    provider = provider.lower().strip()
    
    if provider == "stub":
        return NotImplementedVisionEngine()
    
    elif provider == "tesseract":
        try:
            from app.core.vision.tesseract import TesseractVisionEngine
            return TesseractVisionEngine(lang="eng+khm")
        except ImportError as e:
            raise ImportError(
                f"Tesseract provider requires: pip install pytesseract pillow\n"
                f"And Tesseract installation. See app/core/vision/tesseract.py for details."
            ) from e
    
    elif provider == "mathpix":
        try:
            from app.core.vision.mathpix import MathpixVisionEngine
            return MathpixVisionEngine()
        except ImportError as e:
            raise ImportError(
                f"Mathpix provider requires: pip install requests\n"
                f"And MATHPIX_APP_ID, MATHPIX_APP_KEY environment variables."
            ) from e
    
    elif provider == "google" or provider == "google_vision":
        try:
            from app.core.vision.google_vision import GoogleVisionEngine
            return GoogleVisionEngine()
        except ImportError as e:
            raise ImportError(
                f"Google Vision provider requires: pip install google-cloud-vision\n"
                f"And GOOGLE_APPLICATION_CREDENTIALS environment variable."
            ) from e
    
    else:
        raise ValueError(
            f"Unknown vision provider: {provider}\n"
            f"Available providers: stub, tesseract, mathpix, google"
        )


def list_available_providers() -> dict[str, bool]:
    """
    Check which vision providers are available (have dependencies installed).
    
    Returns:
        Dict mapping provider name to availability (True/False)
    """
    providers = {}
    
    # Stub is always available
    providers["stub"] = True
    
    # Check Tesseract
    try:
        import pytesseract
        from PIL import Image
        pytesseract.get_tesseract_version()
        providers["tesseract"] = True
    except Exception:
        providers["tesseract"] = False
    
    # Check Mathpix
    try:
        import requests
        has_credentials = bool(os.getenv("MATHPIX_APP_ID") and os.getenv("MATHPIX_APP_KEY"))
        providers["mathpix"] = has_credentials
    except ImportError:
        providers["mathpix"] = False
    
    # Check Google Vision
    try:
        from google.cloud import vision
        has_credentials = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        providers["google"] = has_credentials
    except ImportError:
        providers["google"] = False
    
    return providers
