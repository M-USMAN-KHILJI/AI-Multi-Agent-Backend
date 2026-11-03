from typing import Optional, Dict, Any
from app.workflows.graph import image_graph
from app.workflows.state import ImageAgentState

class ImageAgent:
    """
    Image AI Agent powered by LangGraph state machine orchestration:
    - Visual Question Answering & Understanding (Gemini Vision)
    - Image Generation (Gemini prompt enhancement + diffusion engine)
    """
    def __init__(self):
        self.name = "Image AI Agent"
        self.graph = image_graph

    def execute(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Executes the LangGraph state machine for image tasks.
        """
        initial_state: ImageAgentState = {
            "prompt": prompt,
            "image_bytes": image_bytes,
            "mime_type": mime_type,
            "task_type": "understand" if image_bytes else "generate",
            "enhanced_prompt": None,
            "analysis_result": None,
            "generation_result": None,
            "error": None
        }

        # Run compiled LangGraph
        final_state = self.graph.invoke(initial_state)
        return final_state

image_agent = ImageAgent()

