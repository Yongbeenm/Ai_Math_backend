"""
Image preprocessing pipeline for math vision and OCR.

Enhances photos of printed or handwritten math exercises taken by phone
cameras or webcams before passing them to OCR engines (Tesseract, Kiri OCR).

Enhancements:
- EXIF orientation correction (phone camera portrait/landscape)
- Minimum dimension upscaling for small text/superscripts
- Contrast Limited Adaptive Histogram Equalization (CLAHE)
- Edge-preserving denoising
- White margin padding to prevent edge text clipping
"""

from __future__ import annotations

import io
from typing import Literal

import cv2
import numpy as np
from PIL import Image, ImageOps


def preprocess_image(
    image_bytes: bytes,
    mode: Literal["enhanced_grayscale", "binary", "standard"] = "enhanced_grayscale",
    min_dimension: int = 800,
    add_padding: bool = True,
    pad_pixels: int = 25,
) -> bytes:
    """
    Preprocess raw image bytes for optimal OCR recognition.

    Args:
        image_bytes: Raw image file bytes (PNG, JPEG, WebP).
        mode:
            - 'enhanced_grayscale': Grayscale with CLAHE contrast & denoising (recommended for mixed/Khmer OCR)
            - 'binary': Otsu adaptive binarization (black text on pure white background)
            - 'standard': Orientation-corrected and contrast-boosted RGB
        min_dimension: Minimum size (in pixels) for the shorter side; upscaled if smaller.
        add_padding: Whether to add a clean white border around the image.
        pad_pixels: Thickness of white border in pixels.

    Returns:
        Processed image as PNG bytes.
    """
    if not image_bytes:
        return image_bytes

    # 1. Load via PIL to handle EXIF orientation properly
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        # Fallback if image cannot be parsed
        return image_bytes

    # Convert to RGB (dropping alpha channels if any)
    if pil_img.mode in ("RGBA", "LA", "P"):
        rgb_img = Image.new("RGB", pil_img.size, (255, 255, 255))
        if pil_img.mode == "RGBA":
            rgb_img.paste(pil_img, mask=pil_img.split()[3])
        elif pil_img.mode == "LA":
            rgb_img.paste(pil_img, mask=pil_img.split()[1])
        else:
            rgb_img.paste(pil_img.convert("RGB"))
        pil_img = rgb_img
    elif pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    width, height = pil_img.size

    # 2. Upscale if too small (superscripts like x² need sufficient resolution)
    shorter_side = min(width, height)
    if shorter_side < min_dimension and shorter_side > 0:
        scale_factor = min_dimension / shorter_side
        # Cap scaling to 3x to avoid excessive memory usage
        scale_factor = min(scale_factor, 3.0)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert PIL Image to OpenCV numpy array (BGR)
    img_np = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # 3. Mode-specific OpenCV processing
    if mode == "standard":
        # Keep RGB with mild CLAHE on L-channel of LAB
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        final_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        result_img = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)

    else:
        # Grayscale conversions
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Bilateral filter smooths noise while keeping text edges sharp
        denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

        # CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        if mode == "binary":
            # Otsu's automatic thresholding
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            result_img = binary
        else:
            result_img = enhanced

    # 4. Add white padding around borders
    if add_padding and pad_pixels > 0:
        if len(result_img.shape) == 2:
            result_img = cv2.copyMakeBorder(
                result_img,
                top=pad_pixels,
                bottom=pad_pixels,
                left=pad_pixels,
                right=pad_pixels,
                borderType=cv2.BORDER_CONSTANT,
                value=[255, 255, 255],
            )
        else:
            result_img = cv2.copyMakeBorder(
                result_img,
                top=pad_pixels,
                bottom=pad_pixels,
                left=pad_pixels,
                right=pad_pixels,
                borderType=cv2.BORDER_CONSTANT,
                value=[255, 255, 255],
            )

    # 5. Encode back to PNG bytes
    success, encoded_img = cv2.imencode(".png", result_img)
    if not success:
        return image_bytes

    return encoded_img.tobytes()
