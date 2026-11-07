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

    # NVIDIA Vision Configuration (Google PaliGemma VLM)
    NVIDIA_VISION_API_KEY: str = os.getenv("NVIDIA_VISION_API_KEY", "")
    NVIDIA_VISION_MODEL: str = os.getenv("NVIDIA_VISION_MODEL", "google/paligemma")
    NVIDIA_VISION_URL: str = os.getenv("NVIDIA_VISION_URL", "https://ai.api.nvidia.com/v1/vlm/google/paligemma")

    # NVIDIA GenAI Configuration (FLUX 3 Image Klein)
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_FLUX_URL: str = os.getenv("NVIDIA_FLUX_URL", "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-3-image-klein")

    # Hugging Face Video Generation Configuration (Lightricks LTX-Video)
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HF_VIDEO_MODEL: str = os.getenv("HF_VIDEO_MODEL", "Lightricks/ltx-video-distilled")

    # ElevenLabs Voice TTS Configuration
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Sarah: Mature, Reassuring, Confident
    ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

    # NVIDIA Resemble.AI Chatterbox Multilingual TTS
    NVIDIA_TTS_API_KEY: str = os.getenv("NVIDIA_TTS_API_KEY", "")
    NVIDIA_TTS_SERVER: str = os.getenv("NVIDIA_TTS_SERVER", "grpc.nvcf.nvidia.com:443")
    NVIDIA_TTS_FUNCTION_ID: str = os.getenv("NVIDIA_TTS_FUNCTION_ID", "ddacc747-1269-4fab-bfd9-8f593dead106")
    NVIDIA_TTS_VOICE: str = os.getenv("NVIDIA_TTS_VOICE", "Chatterbox-Multilingual.en-US.Male")

    # Storage Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "uploads")
    GENERATED_DIR: str = os.path.join(BASE_DIR, "generated")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

settings = Settings()
