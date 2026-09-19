"""
Tesseract OCR integration (open-source, offline).

Tesseract is a free, open-source OCR engine that can run locally without
internet connection. It's good for printed text but less accurate for
handwriting. Best used for development/testing or when privacy is critical.

Setup:
1. Install Tesseract:
   - macOS: brew install tesseract
   - Ubuntu: sudo apt-get install tesseract-ocr
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Python wrapper: pip install pytesseract pillow
3. (Optional) Install Khmer language data:
   - Download from: https://github.com/tesseract-ocr/tessdata
   - Place khm.traineddata in Tesseract tessdata directory

Documentation: https://github.com/tesseract-ocr/tesseract
"""
from __future__ import annotations

from io import BytesIO

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from app.core.vision.base import MathVisionEngine, VisionResult


class TesseractVisionEngine(MathVisionEngine):
    """
    OCR using Tesseract (offline, open-source).
    
    Pros:
    - Free and open-source
    - Works offline (no internet needed)
    - No API limits or costs
    - Privacy-friendly (data stays local)
    - Supports Khmer language
    
    Cons:
    - Less accurate for handwriting
    - Struggles with complex math notation
    - Slower than cloud services
    - Requires local installation
    """
    
    def __init__(self, lang: str = "eng+khm"):
        """
        Initialize Tesseract engine.
        
        Args:
            lang: Language codes (e.g., "eng" for English, "khm" for Khmer,
                  "eng+khm" for both). Use tesseract --list-langs to see available.
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "pytesseract and PIL required. "
                "Install with: pip install pytesseract pillow"
            )
        
        self.lang = lang
        
        # Verify Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            raise RuntimeError(
                "Tesseract not found. Install it:\n"
                "- macOS: brew install tesseract\n"
                "- Ubuntu: sudo apt-get install tesseract-ocr\n"
                "- Windows: https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Use Tesseract to detect text in image.
        """
        try:
            # Open image from bytes
            image = Image.open(BytesIO(image_bytes))
            
            # Configure Tesseract for better math/number recognition
            custom_config = r'--oem 3 --psm 6'  # Use LSTM, assume uniform block of text
            
            # Perform OCR
            detected_text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=custom_config
            ).strip()
            
            # Get confidence data
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence (filter out -1 values)
            confidences = [
                float(conf) / 100.0 
                for conf in data['conf'] 
                if conf != -1
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            if not detected_text:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="No text detected in image"
                )
            
            return VisionResult(
                detected_text=detected_text,
                confidence=avg_confidence,
                error_message=None
            )
            
        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"Tesseract error: {str(e)}"
            )
