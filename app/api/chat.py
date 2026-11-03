from fastapi import APIRouter, HTTPException, status
from app.schemas.chat_schema import TextChatRequest, TextChatResponse
from app.agents.text_agent import text_agent

router = APIRouter(prefix="/chat", tags=["Text AI Agent"])

@router.post("/text", response_model=TextChatResponse, status_code=status.HTTP_200_OK)
def handle_text_chat(request: TextChatRequest):
    """
    Direct endpoint for interacting with the Text AI Agent.
    Accepts prompt, optional conversation history, and model parameters.
    """
    try:
        history_dicts = [msg.model_dump() for msg in request.history] if request.history else []
        result = text_agent.process(
            user_message=request.message,
            conversation_history=history_dicts,
            custom_system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return TextChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text AI Agent generation error: {str(e)}"
        )

