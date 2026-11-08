import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.images import router as images_router
from app.api.videos import router as videos_router
from app.api.audio import router as audio_router

def create_application() -> FastAPI:
    """
    FastAPI Application Factory.
    Initializes middleware, static asset serving, and routers.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Unified Multimodal Multi-Agent AI Platform Backend with LangGraph and FastAPI.",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files mounting for generated assets (images, videos, audio)
    os.makedirs(settings.GENERATED_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.GENERATED_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.GENERATED_DIR, "videos"), exist_ok=True)
    os.makedirs(os.path.join(settings.GENERATED_DIR, "audio"), exist_ok=True)
    app.mount("/generated", StaticFiles(directory=settings.GENERATED_DIR), name="generated")

    # Register Routers (Mount at root /api/v1)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(images_router, prefix="/api/v1")
    app.include_router(videos_router, prefix="/api/v1")
    app.include_router(audio_router, prefix="/api/v1")

    # Also register at /api/index/api/v1 to natively support Vercel CLI 65 rewrite paths
    app.include_router(health_router, prefix="/api/index/api/v1")
    app.include_router(chat_router, prefix="/api/index/api/v1")
    app.include_router(images_router, prefix="/api/index/api/v1")
    app.include_router(videos_router, prefix="/api/index/api/v1")
    app.include_router(audio_router, prefix="/api/index/api/v1")

    @app.get("/")
    @app.get("/api/index")
    def root():
        return {
            "platform": settings.PROJECT_NAME,
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/api/v1/health"
        }

    return app

app = create_application()
