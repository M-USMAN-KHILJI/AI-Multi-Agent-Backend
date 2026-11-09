from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessagePayload(BaseModel):
    role: str = Field(..., description="Role of the author: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")

class TextChatRequest(BaseModel):
    message: str = Field(..., description="User prompt or question")
    history: Optional[List[MessagePayload]] = Field(default_factory=list, description="Prior conversation messages")
    system_prompt: Optional[str] = Field(default=None, description="Custom system instruction override")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1024, ge=1, le=4096)
    user_name: Optional[str] = Field(default=None, description="User's display name or identifier")
    user_email: Optional[str] = Field(default=None, description="User's email address")
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")

class TextChatResponse(BaseModel):
    response: str = Field(..., description="Generated text response from Text AI Agent")
    agent_name: str = Field(default="Text AI Agent")
    model: str = Field(..., description="Model identifier used for generation")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Token consumption metrics")
    session_id: Optional[str] = Field(default=None, description="Database conversation session ID")
