"""
LaTeX-OCR (pix2tex) vision engine for mathematical formula recognition.

Uses Lukas Blecher's LaTeX-OCR (ViT + ResNet encoder-decoder) to transcribe
cropped images of mathematical equations directly into LaTeX code.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image

from app.ocr.extraction.base import MathVisionEngine, VisionResult


def clean_pix2tex_output(latex_code: str) -> str:
    """Clean and normalize raw LaTeX output from pix2tex."""
    import re

    t = (latex_code or "").strip()
    # Strip leading label artifacts like \mathcal{Q}. or 2. or a. or (a) before a formula
    t = re.sub(
        r"^\s*(?:"
        r"\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?"
        r"|(?:[\\/](?:mathcal|mathbf|mathrm|text)\{[a-zA-Z0-9\u1780-\u17a2]+\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d)"
        r")\s*",
        "",
        t,
    )
    # Strip trailing LaTeX spacing tokens and punctuation like \; \, \! \quad
    t = re.sub(r"(\\[;,!]|\\quad|\\qquad|[\s;.,])+$", "", t)
    # Normalize \operatorname*{lim} or \operatorname{lim}
    t = t.replace(r"\operatorname*{lim}", r"\lim").replace(r"\operatorname{lim}", r"\lim")
    # Clean spaces inside trig functions from OCR (e.g. 's i n' or 'c o s' or 't a n')
    t = t.replace("s i n", r"\sin").replace("c o s", r"\cos").replace("t a n", r"\tan")
    # Normalize Greek letter chi to x when used as variable
    t = re.sub(r"\\chi\b", "x", t)
    # Remove rogue aleph, kappa, or noisy superscript artifacts from OCR
    t = re.sub(r"\^\{?\\(aleph|kappa)\}?", "^", t)
    # Clean escaped spaces like '\ 15'
    t = re.sub(r"\\[\s]+", " ", t)
    # Normalize \times recognized as variable x (e.g. 12\times=25 -> 12x=25)
    t = re.sub(r"(?<=\d)\\times(?=[=+\-*/<>]|\s|$)", "x", t)
    if "lim_{" in t and r"\lim_{" not in t:
        t = t.replace("lim_{", r"\lim_{")
    return t.strip()


class Pix2TexVisionEngine(MathVisionEngine):
    """
    Formula OCR using pix2tex (LaTeX-OCR).

    Pros:
    - Open-source, runs offline
    - Converts mathematical notation directly into LaTeX code
    - Excellent for fractions, integrals, limits, exponents, roots

    Cons:
    - Designed specifically for isolated math formulas, not prose or Khmer words
    """

    def __init__(self, model_instance: Any | None = None):
        self._model = model_instance

    @property
    def model(self) -> Any:
        """Lazy load model weights so app startup remains fast."""
        if self._model is None:
            from pix2tex.cli import LatexOCR

            self._model = LatexOCR()
        return self._model

    def detect(self, image_bytes: bytes) -> VisionResult:
        if not image_bytes:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message="Image data is empty",
            )

        try:
            img = Image.open(BytesIO(image_bytes))
            raw_latex = self.model(img)
            latex_code = clean_pix2tex_output(raw_latex)

            if not latex_code:
                return VisionResult(
                    detected_text=None,
                    confidence=0.0,
                    error_message="No formula detected by LaTeX-OCR",
                )

            from app.core.khmer.exercise_parser import parse_exercise

            parsed_ex = parse_exercise(latex_code)
            clean_expr = parsed_ex.primary_expression or latex_code

            return VisionResult(
                detected_text=latex_code,
                confidence=0.95,
                error_message=None,
                exercise_metadata={
                    "exercise_title": parsed_ex.exercise_title,
                    "instruction": parsed_ex.instruction,
                    "primary_expression": clean_expr,
                    "sub_exercises": [
                        {
                            "label": s.label,
                            "raw_text": s.raw_text,
                            "expression": s.expression,
                            "intent": s.intent,
                        }
                        for s in parsed_ex.sub_exercises
                    ],
                },
            )

        except Exception as e:
            return VisionResult(
                detected_text=None,
                confidence=0.0,
                error_message=f"LaTeX-OCR (pix2tex) error: {str(e)}",
            )
