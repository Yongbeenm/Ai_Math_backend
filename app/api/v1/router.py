from fastapi import APIRouter

from app.api.v1.endpoints import health, history, parse, solve, vision

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(solve.router)
api_router.include_router(parse.router)
api_router.include_router(vision.router)
api_router.include_router(history.router)
