from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import User, ChatSession, ChatMessage

class UserRepository:
    @staticmethod
    def get_or_create(db: Session, name: str, email: Optional[str] = None) -> User:
        user = None
        if email:
            user = db.query(User).filter(User.email == email.strip().lower()).first()
        if not user:
            user = db.query(User).filter(User.name == name.strip()).first()
        if not user:
            user = User(
                name=name.strip(),
                email=email.strip().lower() if email else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

class ChatRepository:
    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    @staticmethod
    def create_or_get_session(
        db: Session,
        session_id: str,
        title: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatSession:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                title=title or "New Conversation",
                user_id=user_id
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        elif user_id and not session.user_id:
            session.user_id = user_id
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def add_message(
        db: Session,
        session_id: str,
        sender: str,
        text: Optional[str],
        modality: str = "text",
        agent_name: Optional[str] = None,
        routing_reason: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ) -> ChatMessage:
        msg = ChatMessage(
            id=message_id,
            session_id=session_id,
            sender=sender,
            text=text,
            modality=modality,
            agent_name=agent_name,
            routing_reason=routing_reason,
            meta_info=meta_info
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_messages(db: Session, session_id: str) -> List[ChatMessage]:
        return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()

    @staticmethod
    def get_user_sessions(db: Session, user_id: str) -> List[ChatSession]:
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()

