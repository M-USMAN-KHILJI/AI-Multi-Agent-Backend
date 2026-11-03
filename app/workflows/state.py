from typing import TypedDict, Optional, Dict, Any

class ImageAgentState(TypedDict):
    """
    State schema for the Image AI Agent LangGraph workflow.
    Tracks input prompt, attached image bytes, task classification, and outputs.
    """
    prompt: str
    image_bytes: Optional[bytes]
    mime_type: Optional[str]
    task_type: str  # 'understand' | 'generate'
    enhanced_prompt: Optional[str]
    analysis_result: Optional[str]
    generation_result: Optional[Dict[str, Any]]
    error: Optional[str]

