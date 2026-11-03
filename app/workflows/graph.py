"""
LangGraph State Machine for the Image AI Agent.
Routes dynamically between Visual Understanding (Gemini VQA) and Image Generation.
"""
from langgraph.graph import StateGraph, END
from app.workflows.state import ImageAgentState
from app.services.image_service import image_service

def route_image_task(state: ImageAgentState) -> str:
    """
    Conditional Edge Evaluator:
    - If image_bytes are provided, route to the 'understand_node' (Gemini Vision).
    - Otherwise, route to the 'generate_node' (Diffusion generation).
    """
    if state.get("image_bytes"):
        return "understand_node"
    return "generate_node"

def understand_node(state: ImageAgentState) -> ImageAgentState:
    """
    LangGraph Node: Visual Understanding via Google Gemini 2.5 Flash Vision.
    """
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
    """
    LangGraph Node: Prompt Enhancement + Image Synthesis.
    """
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
    """
    Compiles the LangGraph State Graph for the Image AI Agent.
    """
    workflow = StateGraph(ImageAgentState)

    # Add execution nodes
    workflow.add_node("understand_node", understand_node)
    workflow.add_node("generate_node", generate_node)

    # Set conditional entry edge
    workflow.set_conditional_entry_point(
        route_image_task,
        {
            "understand_node": "understand_node",
            "generate_node": "generate_node"
        }
    )

    # Normal finish edges
    workflow.add_edge("understand_node", END)
    workflow.add_edge("generate_node", END)

    return workflow.compile()

image_graph = build_image_graph()

