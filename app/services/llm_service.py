from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings

class LLMService:
    """
    Dedicated LLM inference service communicating with Groq / OpenAI-compatible APIs.
    """
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.GROQ_BASE_URL,
            api_key=settings.GROQ_API_KEY,
            timeout=30.0
        )
        self.default_model = settings.GROQ_DEFAULT_MODEL

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Executes a synchronous chat completion call.
        """
        selected_model = model or self.default_model
        response = self.client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        usage_data = None
        if response.usage:
            usage_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

        return {
            "content": response.choices[0].message.content,
            "model": response.model or selected_model,
            "usage": usage_data
        }

llm_service = LLMService()

