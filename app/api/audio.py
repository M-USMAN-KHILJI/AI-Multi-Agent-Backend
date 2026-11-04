from fastapi import APIRouter, HTTPException, status
from app.schemas.audio_schema import TTSRequest, TTSResponse
from app.services.audio_service import audio_service

router = APIRouter(prefix="/audio", tags=["Audio AI Agent"])

@router.post("/tts", response_model=TTSResponse, status_code=status.HTTP_200_OK)
def text_to_speech_endpoint(request: TTSRequest):
    """
    Synthesize text into speech WAV audio via NVIDIA Resemble AI Chatterbox Multilingual TTS.
    """
    try:
        res = audio_service.synthesize_speech(
            text=request.text,
            voice_name=request.voice,
            language_code=request.language_code or "en-US"
        )

        return TTSResponse(
            audio_url=res["url"],
            filename=res["filename"],
            text=res["text"],
            voice=res["voice"],
            language_code=res["language_code"],
            size_bytes=res["size_bytes"],
            model=res["model"],
            status=res["status"]
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS synthesis error: {str(e)}"
        )

