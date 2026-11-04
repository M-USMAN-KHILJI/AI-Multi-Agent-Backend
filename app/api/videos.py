from fastapi import APIRouter, HTTPException, status
from app.schemas.video_schema import VideoGenerateRequest, VideoGenerateResponse
from app.agents.video_agent import video_agent

router = APIRouter(prefix="/videos", tags=["Video AI Agent"])

@router.post("/generate", response_model=VideoGenerateResponse, status_code=status.HTTP_200_OK)
def generate_video_endpoint(request: VideoGenerateRequest):
    """
    Generate a 2-second video clip from a text prompt via LangGraph & Hugging Face Drishya-Tiny.
    """
    try:
        state = video_agent.execute(
            prompt=request.prompt,
            seed=request.seed if request.seed is not None else -1
        )

        if state.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video generation error: {state['error']}"
            )

        res = state.get("video_result")
        if not res:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No video was produced by the generator."
            )

        return VideoGenerateResponse(
            video_url=res["url"],
            filename=res["filename"],
            prompt=res["prompt"],
            model=res["model"],
            size_bytes=res["size_bytes"],
            duration_seconds=res["duration_seconds"],
            status=res["status"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video endpoint error: {str(e)}"
        )

