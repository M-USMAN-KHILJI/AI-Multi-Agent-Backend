# OmniAgent AI Platform — Backend

Enterprise-grade multimodal multi-agent backend built with FastAPI, LangGraph, and specialized AI models (Groq, NVIDIA FLUX 3, PaliGemma, ElevenLabs, Lightricks LTX-Video).

---

## Deploy on Railway

This repository is containerized and configured for deployment on [Railway](https://railway.com) without any manual build steps.

### Step 1: Deploy from GitHub Repo
1. Go to your **Railway Dashboard** and click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
2. Select this repository: `AI-Multi-Agent-Backend`.
3. Railway automatically detects the root `Dockerfile` and builds the image.

### Step 2: Configure Environment Variables
In Railway, navigate to your service $\rightarrow$ **Variables** tab, and add the following:

| Variable | Description | Example / Default |
|---|---|---|
| `ENVIRONMENT` | Application environment | `production` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `*` or `https://your-frontend.vercel.app` |
| `GROQ_API_KEY` | Groq Cloud LPU key for Text AI Agent | `gsk_...` |
| `GEMINI_API_KEY` | Google Gemini API key for vision/prompts | `AIza...` |
| `NVIDIA_API_KEY` | NVIDIA GenAI key (FLUX 3 Image Klein) | `nvapi-...` |
| `NVIDIA_VISION_API_KEY` | NVIDIA Vision key (Google PaliGemma VLM) | `nvapi-...` |
| `HUGGINGFACE_API_KEY` | Hugging Face token for LTX-Video synthesis | `hf_...` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for Neural TTS | `sk_...` |
| `ELEVENLABS_VOICE_ID` | ElevenLabs Voice ID (Sarah) | `EXAVITQu4vr4xnSDxMaL` |
| `ELEVENLABS_MODEL_ID` | ElevenLabs Model | `eleven_multilingual_v2` |
| `NVIDIA_TTS_API_KEY` | NVIDIA Riva TTS key (fallback) | `nvapi-...` |
| `DATABASE_URL` | PostgreSQL connection string | Optional (e.g. `${{Postgres.DATABASE_URL}}`) |

*Note: Railway automatically injects `PORT`. The container dynamically binds `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.*

### Step 3: Healthcheck & Verification
- **Healthcheck Path:** `/api/v1/health` (returns `HTTP 200` without requiring API keys)
- **Interactive Documentation:** `/docs` (Swagger UI)
