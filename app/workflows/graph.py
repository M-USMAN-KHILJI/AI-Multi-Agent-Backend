"""
LangGraph State Machines for Multimodal AI Agents:
- Image AI Agent: Routes between Visual Understanding (PaliGemma) and Synthesis (FLUX 3).
- Video AI Agent: Generates text-to-video clips via Hugging Face Drishya-Tiny.
"""
from langgraph.graph import StateGraph, END
from app.workflows.state import ImageAgentState, VideoAgentState
from app.services.image_service import image_service
from app.services.video_service import video_service

# ── IMAGE GRAPH ──
def route_image_task(state: ImageAgentState) -> str:
    if state.get("image_bytes"):
        return "understand_node"
    return "generate_node"

def understand_node(state: ImageAgentState) -> ImageAgentState:
    try:
        analysis = image_service.analyze_image(
            prompt=state.get("prompt", ""),
            image_bytes=state["image_bytes"],
            mime_type=state.get("mime_type", "image/jpeg")
        )
        return {
            **state,
            "task_type": "understand",
            "analysis_result": analysis
        }
    except Exception as e:
        return {
            **state,
            "task_type": "understand",
            "error": str(e)
        }

def generate_node(state: ImageAgentState) -> ImageAgentState:
    try:
        gen_data = image_service.generate_image(
            prompt=state.get("prompt", "")
        )
        return {
            **state,
            "task_type": "generate",
            "enhanced_prompt": gen_data.get("enhanced_prompt"),
            "generation_result": gen_data
        }
    except Exception as e:
        return {
            **state,
            "task_type": "generate",
            "error": str(e)
        }

def build_image_graph():
    workflow = StateGraph(ImageAgentState)
    workflow.add_node("understand_node", understand_node)
    workflow.add_node("generate_node", generate_node)
    workflow.set_conditional_entry_point(
        route_image_task,
        {
            "understand_node": "understand_node",
            "generate_node": "generate_node"
        }
    )
    workflow.add_edge("understand_node", END)
    workflow.add_edge("generate_node", END)
    return workflow.compile()

image_graph = build_image_graph()

# ── VIDEO GRAPH ──
def video_generate_node(state: VideoAgentState) -> VideoAgentState:
    try:
        video_data = video_service.generate_video(
            prompt=state.get("prompt", ""),
            seed=state.get("seed", -1)
        )
        return {
            **state,
            "video_result": video_data,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "video_result": None,
            "error": str(e)
        }

def build_video_graph():
    workflow = StateGraph(VideoAgentState)
    workflow.add_node("generate_video_node", video_generate_node)
    workflow.set_entry_point("generate_video_node")
    workflow.add_edge("generate_video_node", END)
    return workflow.compile()

video_graph = build_video_graph()
