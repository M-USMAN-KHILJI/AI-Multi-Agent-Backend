from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from app.schemas.image_schema import ImageGenerateRequest, ImageGenerateResponse, ImageAnalyzeResponse
from app.agents.image_agent import image_agent
from app.services.image_service import image_service

router = APIRouter(prefix="/images", tags=["Image AI Agent"])

@router.post("/generate", response_model=ImageGenerateResponse, status_code=status.HTTP_200_OK)
def generate_image_endpoint(request: ImageGenerateRequest):
    """
    Generate a new image from a text prompt via LangGraph Image Agent & NVIDIA FLUX 3 Image Klein.
    """
    try:
        state = image_agent.execute(prompt=request.prompt)
        if state.get("error"):
            raise HTTPException(status_code=500, detail=state["error"])

        gen = state["generation_result"]
        return ImageGenerateResponse(
            image_url=gen["url"],
            filename=gen["filename"],
            original_prompt=gen["original_prompt"],
            enhanced_prompt=gen["enhanced_prompt"],
            width=gen["width"],
            height=gen["height"],
            size_bytes=gen["size_bytes"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation error: {str(e)}"
        )

@router.post("/analyze", response_model=ImageAnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_image_endpoint(
    prompt: Optional[str] = Form("Inspect this image in detail and describe what you see."),
    file: UploadFile = File(...)
):
    """
    Upload an image and ask a question about it.
    Processed by NVIDIA Multimodal Vision via LangGraph.
    """
    try:
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"

        state = image_agent.execute(
            prompt=prompt,
            image_bytes=image_bytes,
            mime_type=mime_type
        )

        if state.get("error"):
            raise HTTPException(status_code=500, detail=state["error"])

        return ImageAnalyzeResponse(
            analysis=state["analysis_result"],
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis error: {str(e)}"
        )

@router.post("/edit", response_model=ImageGenerateResponse, status_code=status.HTTP_200_OK)
async def edit_image_endpoint(
    instruction: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload an original image + instruction for modifications.
    Understands original image with NVIDIA Vision and synthesizes the updated image via NVIDIA FLUX 3.
    """
    try:
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"

        gen = image_service.edit_image_with_prompt(
            user_instruction=instruction,
            original_image_bytes=image_bytes,
            mime_type=mime_type
        )

        return ImageGenerateResponse(
            image_url=gen["url"],
            filename=gen["filename"],
            original_prompt=gen.get("original_image_description", instruction),
            enhanced_prompt=gen.get("enhanced_prompt", instruction),
            width=gen["width"],
            height=gen["height"],
            size_bytes=gen["size_bytes"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image edit error: {str(e)}"
        )
