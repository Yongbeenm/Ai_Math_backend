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
        
        For Kiri OCR (Khmer & English):
            (none needed - models download on first run)
    
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
    
    elif provider in ("kiri", "kiri_ocr", "khmer_ocr"):
        try:
            from app.core.vision.kiri_ocr import KiriVisionEngine
            return KiriVisionEngine()
        except ImportError as e:
            raise ImportError(
                f"Kiri Khmer OCR provider requires: pip install kiri-ocr\n"
                f"See app/core/vision/kiri_ocr.py for details."
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
    
    elif provider == "gemini":
        try:
            from app.core.vision.gemini_vision import GeminiVisionEngine
            return GeminiVisionEngine()
        except Exception as e:
            raise ValueError(
                f"Gemini Vision provider requires GEMINI_API_KEY in .env: {e}"
            ) from e

    elif provider in ("pix2tex", "latex_ocr", "latex"):
        try:
            from app.core.vision.pix2tex_engine import Pix2TexVisionEngine
            return Pix2TexVisionEngine()
        except ImportError as e:
            raise ImportError(
                f"LaTeX-OCR provider requires: pip install pix2tex\n"
                f"See app/core/vision/pix2tex_engine.py for details."
            ) from e

    else:
        raise ValueError(
            f"Unknown vision provider: {provider}\n"
            f"Available providers: stub, tesseract, kiri (khmer_ocr), pix2tex (latex_ocr), mathpix, google, gemini"
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
    
    # Check Kiri OCR (Khmer)
    try:
        from app.core.vision.kiri_ocr import KIRI_OCR_AVAILABLE
        providers["kiri"] = KIRI_OCR_AVAILABLE
        providers["khmer_ocr"] = KIRI_OCR_AVAILABLE
    except Exception:
        providers["kiri"] = False
        providers["khmer_ocr"] = False

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

    # Check Gemini
    providers["gemini"] = bool(os.getenv("GEMINI_API_KEY"))

    # Check LaTeX-OCR (pix2tex)
    try:
        import pix2tex
        providers["pix2tex"] = True
        providers["latex_ocr"] = True
    except ImportError:
        providers["pix2tex"] = False
        providers["latex_ocr"] = False

    return providers
