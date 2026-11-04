import os
import sys
import time

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.agents.video_agent import video_agent

client = TestClient(app)

def safe_print(text: str):
    """Safely print text handling Windows console limitations."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def test_video_generation_direct():
    """Verify VideoAgent LangGraph generates a video clip via Lightricks LTX-Video."""
    safe_print("\n[TEST 1] Testing VideoAgent direct execution via LangGraph & LTX-Video...")
    prompt = "A cinematic shot of a drone flying through a misty forest at sunrise"
    result = video_agent.execute(prompt=prompt)

    assert result.get("error") is None, f"Video generation failed: {result.get('error')}"
    res = result.get("video_result")
    assert res is not None, "video_result should not be None"
    assert os.path.exists(res["file_path"]), f"Generated video file should exist: {res['file_path']}"
    assert res["size_bytes"] > 10000, f"Video size should be > 10KB, got {res['size_bytes']}"
    assert res["url"].startswith("/generated/videos/"), f"URL should be valid: {res['url']}"
    safe_print(f"[PASS] Video generated: {res['filename']} ({res['size_bytes']} bytes, 704x512, {res['duration_seconds']}s)")

def test_video_api_endpoint():
    """Verify FastAPI POST /api/v1/videos/generate endpoint."""
    safe_print("\n[TEST 2] Testing /api/v1/videos/generate HTTP POST endpoint...")
    prompt = "Ocean waves crashing on a sandy beach at golden sunset"
    res = client.post("/api/v1/videos/generate", json={"prompt": prompt, "seed": -1})
    assert res.status_code == 200, f"Generate endpoint failed: {res.text}"
    body = res.json()
    assert body["status"] == "success"
    assert "video_url" in body
    assert body["size_bytes"] > 10000
    safe_print(f"[PASS] Endpoint response 200: {body['video_url']} ({body['size_bytes']} bytes)")

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("STARTING LIGHTRICKS LTX-VIDEO UNIT TESTS")
    safe_print("=" * 60)
    test_video_generation_direct()
    test_video_api_endpoint()
    safe_print("=" * 60)
    safe_print("ALL LTX-VIDEO UNIT TESTS PASSED!")
    safe_print("=" * 60)
