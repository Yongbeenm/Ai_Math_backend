"""
Application entrypoint. Run with:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then open http://127.0.0.1:8000/docs for interactive API docs.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.db.init_db import init_models

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path

from fastapi.staticfiles import StaticFiles

app.include_router(api_router, prefix=settings.api_v1_prefix)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists() and (frontend_dir / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    @app.get("/")
    def root() -> dict:
        return {"app": settings.app_name, "version": settings.app_version, "docs": "/docs"}
