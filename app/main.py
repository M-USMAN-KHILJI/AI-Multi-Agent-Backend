import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.images import router as images_router

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

    # Static files mounting for generated assets (images, audio previews, video frames)
    os.makedirs(settings.GENERATED_DIR, exist_ok=True)
    app.mount("/generated", StaticFiles(directory=settings.GENERATED_DIR), name="generated")

    # Register Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(images_router, prefix="/api/v1")

    @app.get("/")
    def root():
        return {
            "platform": settings.PROJECT_NAME,
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/api/v1/health"
        }

    return app

app = create_application()
