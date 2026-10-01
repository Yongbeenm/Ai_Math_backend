"""
Custom application exception hierarchy.
Re-exported from app.utils.exceptions for single source of truth and backward compatibility.
"""
from __future__ import annotations

from app.utils.exceptions import (
    AppException,
    EntityNotFoundError,
    MathProcessingError,
    VisionProcessingError,
)

__all__ = [
    "AppException",
    "EntityNotFoundError",
    "MathProcessingError",
    "VisionProcessingError",
]
