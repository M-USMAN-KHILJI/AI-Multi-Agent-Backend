from pydantic import BaseModel, Field
from typing import Optional

class VideoGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt describing the video to generate", min_length=2)
    seed: Optional[int] = Field(-1, description="Random seed (-1 for random)")

class VideoGenerateResponse(BaseModel):
    video_url: str
    filename: str
    prompt: str
    model: str
    size_bytes: int
    duration_seconds: float
    status: str

