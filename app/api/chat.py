import uuid
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.chat_schema import TextChatRequest, TextChatResponse
from app.agents.text_agent import text_agent
from app.database.connection import get_db, SessionLocal
from app.database.repositories import UserRepository, ChatRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Text AI Agent"])

@router.post("/text", response_model=TextChatResponse, status_code=status.HTTP_200_OK)
def handle_text_chat(request: TextChatRequest, db: Session = Depends(get_db)):
    """
    Direct endpoint for interacting with the Text AI Agent.
    Accepts prompt, optional conversation history, user info, and model parameters.
    Saves User, Session, User message, and Assistant response directly to PostgreSQL (modeldb).
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

        # Database persistence
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:12]}"
        try:
            user = None
            if request.user_name or request.user_email:
                user = UserRepository.get_or_create(
                    db=db,
                    name=request.user_name or "Anonymous User",
                    email=request.user_email
                )

            # Create or update chat session
            chat_session = ChatRepository.create_or_get_session(
                db=db,
                session_id=session_id,
                title=request.message[:45] + ("..." if len(request.message) > 45 else ""),
                user_id=user.id if user else None
            )

            # Save user prompt
            ChatRepository.add_message(
                db=db,
                session_id=chat_session.id,
                sender="user",
                text=request.message,
                modality="text",
                agent_name="User"
            )

            # Save assistant response
            ChatRepository.add_message(
                db=db,
                session_id=chat_session.id,
                sender="assistant",
                text=result["response"],
                modality="text",
                agent_name=result.get("agent_name", "Text AI Agent"),
                meta_info={
                    "model": result.get("model"),
                    "usage": result.get("usage")
                }
            )
            logger.info(f"Saved conversation message to modeldb for session: {session_id}")
        except Exception as db_err:
            logger.warning(f"Failed to persist chat message to database: {db_err}")

        return TextChatResponse(
            response=result["response"],
            agent_name=result.get("agent_name", "Text AI Agent"),
            model=result.get("model", ""),
            usage=result.get("usage"),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text AI Agent generation error: {str(e)}"
        )

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve stored chat messages from PostgreSQL for a given session.
    """
    messages = ChatRepository.get_messages(db, session_id)
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "text": msg.text,
                "modality": msg.modality,
                "agent_name": msg.agent_name,
                "routing_reason": msg.routing_reason,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    }
