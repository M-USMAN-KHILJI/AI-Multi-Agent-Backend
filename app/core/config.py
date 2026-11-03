import os
from typing import List
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "OmniAgent AI Platform")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:901a8520@localhost:5432/modeldb"
    )

    # Groq LLM Configuration (Text AI Agent)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_DEFAULT_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "openai/gpt-oss-120b")

    # Google Gemini Configuration (Vision Understanding & Prompt Synthesis)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # NVIDIA GenAI Configuration (FLUX 3 Image Klein)
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_FLUX_URL: str = os.getenv("NVIDIA_FLUX_URL", "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-3-image-klein")

    # Storage Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "uploads")
    GENERATED_DIR: str = os.path.join(BASE_DIR, "generated")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

settings = Settings()
