from pydantic import BaseModel, Field
from typing import Optional

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text content to be synthesized to speech", min_length=1)
    voice: Optional[str] = Field("EXAVITQu4vr4xnSDxMaL", description="Voice profile ID (default: Sarah)")
    language_code: Optional[str] = Field("en-US", description="Target language code (e.g. en-US, es-US, hi-IN)")

class TTSResponse(BaseModel):
    audio_url: str
    filename: str
    text: str
    voice: str
    language_code: str
    size_bytes: int
    model: str
    status: str

