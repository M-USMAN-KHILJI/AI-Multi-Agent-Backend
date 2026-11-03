from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Description of the image to generate")
    width: Optional[int] = Field(default=1024, ge=256, le=2048)
    height: Optional[int] = Field(default=1024, ge=256, le=2048)

class ImageGenerateResponse(BaseModel):
    status: str = Field(default="success")
    image_url: str = Field(..., description="Relative URL to the generated image")
    filename: str = Field(..., description="Saved image file name")
    original_prompt: str
    enhanced_prompt: str
    width: int
    height: int
    size_bytes: int

class ImageAnalyzeResponse(BaseModel):
    status: str = Field(default="success")
    analysis: str = Field(..., description="Visual understanding analysis from Google Gemini Vision")
    model: str = Field(default="gemini-2.5-flash")
    filename: Optional[str] = None

