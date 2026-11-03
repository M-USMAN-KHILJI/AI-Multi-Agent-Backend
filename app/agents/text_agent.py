from typing import List, Dict, Any, Optional
from app.services.llm_service import llm_service
from app.prompts.text_prompts import TEXT_AGENT_SYSTEM_PROMPT

class TextAgent:
    """
    Text AI Agent: Handles multi-turn chat, question answering, reasoning, and synthesis.
    """
    def __init__(self):
        self.name = "Text AI Agent"
        self.system_prompt = TEXT_AGENT_SYSTEM_PROMPT

    def process(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        custom_system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Builds message chain and invokes the LLM service.
        """
        messages = []
        
        # 1. System Prompt
        sys_instruction = custom_system_prompt or self.system_prompt
        messages.append({"role": "system", "content": sys_instruction})

        # 2. Conversation History
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # 3. Current User Message
        messages.append({"role": "user", "content": user_message})

        # 4. Generate Completion via LLM Service
        result = llm_service.generate_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "response": result["content"],
            "agent_name": self.name,
            "model": result["model"],
            "usage": result["usage"]
        }

text_agent = TextAgent()

