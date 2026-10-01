"""
API Routes - FastAPI endpoint definitions.

Organized routes:
- /health - Health check
- /math/solve - Solve mathematical problems
- /math/parse - Parse expressions
- /math/vision - OCR and solve from images
- /math/vision/batch - Batch OCR for multi-exercise images
- /history - Solution history

Refactored from app/api/v1/endpoints/ for cleaner organization.
"""

from fastapi import APIRouter

# Import route modules
from app.api.routes import health, history, parse, solve, vision

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(health.router, tags=["health"])
router.include_router(solve.router, prefix="/math", tags=["solve"])
router.include_router(parse.router, prefix="/math", tags=["parse"])
router.include_router(vision.router, prefix="/math", tags=["vision"])
router.include_router(history.router, prefix="/history", tags=["history"])

__all__ = ["router"]
