from typing import Optional, Dict, Any
from app.workflows.graph import video_graph
from app.workflows.state import VideoAgentState

class VideoAgent:
    """
    Video AI Agent powered by LangGraph state machine orchestration:
    - Text-to-Video generation using Hugging Face Drishya-Tiny
    - Local saving and streaming URL provision
    """
    def __init__(self):
        self.name = "Video AI Agent"
        self.graph = video_graph

    def execute(self, prompt: str, seed: int = -1) -> Dict[str, Any]:
        """
        Executes the LangGraph state machine for video generation.
        """
        initial_state: VideoAgentState = {
            "prompt": prompt,
            "seed": seed,
            "video_result": None,
            "error": None
        }

        final_state = self.graph.invoke(initial_state)
        return final_state

video_agent = VideoAgent()

