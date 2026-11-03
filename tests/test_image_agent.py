import os
import sys
import time

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.agents.image_agent import image_agent

client = TestClient(app)

def safe_print(text: str):
    """Safely print text handling Windows console limitations."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def test_image_generation_direct():
    """Verify ImageAgent LangGraph generates a photorealistic image using NVIDIA FLUX 3 Image Klein."""
    safe_print("\n[TEST 1] Testing ImageAgent Image Generation via LangGraph & NVIDIA FLUX 3...")
    prompt = "A high-tech quantum computing core glowing neon blue in an empty server room"
    result = image_agent.execute(prompt=prompt)
    
    assert result["task_type"] == "generate"
    assert result.get("error") is None, f"Generation failed: {result.get('error')}"
    gen = result["generation_result"]
    assert gen is not None
    assert os.path.exists(gen["file_path"]), "Generated image file should exist on disk."
    assert gen["size_bytes"] > 50000, f"Image size should be > 50KB, got {gen['size_bytes']}"
    safe_print(f"[PASS] Image generated: {gen['filename']} ({gen['size_bytes']} bytes)")

def test_image_api_endpoint():
    """Verify FastAPI POST /api/v1/images/generate endpoint with NVIDIA FLUX 3."""
    safe_print("\n[TEST 2] Testing /api/v1/images/generate HTTP POST endpoint...")
    prompt = "A ceramic coffee mug on a wooden desk next to a notebook"
    res = client.post("/api/v1/images/generate", json={"prompt": prompt})
    assert res.status_code == 200, f"Generate endpoint failed: {res.text}"
    body = res.json()
    assert body["status"] == "success"
    assert "image_url" in body
    assert body["size_bytes"] > 50000
    safe_print(f"[PASS] Endpoint response 200: {body['image_url']} ({body['size_bytes']} bytes)")

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("STARTING NVIDIA FLUX 3 IMAGE KLEIN UNIT TESTS")
    safe_print("=" * 60)
    test_image_generation_direct()
    time.sleep(3)  # Brief pause between calls
    test_image_api_endpoint()
    safe_print("\n" + "=" * 60)
    safe_print("ALL NVIDIA FLUX 3 UNIT TESTS PASSED SUCCESSFULLY! [OK]")
    safe_print("=" * 60)
