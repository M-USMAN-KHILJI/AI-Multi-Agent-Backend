import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.audio_service import audio_service

client = TestClient(app)

def safe_print(text: str):
    """Safely print text handling Windows console limitations."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def test_audio_tts_direct():
    """Verify AudioService direct synthesis via NVIDIA Chatterbox TTS."""
    safe_print("\n[TEST 1] Testing AudioService direct synthesis via NVIDIA Chatterbox TTS...")
    text = "Hello! This is a unit test of speech synthesis using NVIDIA Resemble AI."
    res = audio_service.synthesize_speech(text=text)

    assert res["status"] == "success"
    assert os.path.exists(res["file_path"]), f"Generated audio file should exist: {res['file_path']}"
    assert res["size_bytes"] > 50000, f"Audio size should be > 50KB, got {res['size_bytes']}"
    assert res["url"].startswith("/generated/audio/"), f"URL should be valid: {res['url']}"
    safe_print(f"[PASS] Audio generated: {res['filename']} ({res['size_bytes']} bytes, voice: {res['voice']})")

def test_audio_tts_api_endpoint():
    """Verify FastAPI POST /api/v1/audio/tts endpoint."""
    safe_print("\n[TEST 2] Testing /api/v1/audio/tts HTTP POST endpoint...")
    payload = {
        "text": "The multimodal multi-agent system orchestrates distributed tasks seamlessly.",
        "voice": "Chatterbox-Multilingual.en-US.Male",
        "language_code": "en-US"
    }
    res = client.post("/api/v1/audio/tts", json=payload)
    assert res.status_code == 200, f"TTS endpoint failed: {res.text}"
    body = res.json()
    assert body["status"] == "success"
    assert "audio_url" in body
    assert body["size_bytes"] > 50000
    safe_print(f"[PASS] Endpoint response 200: {body['audio_url']} ({body['size_bytes']} bytes)")

if __name__ == "__main__":
    safe_print("=" * 60)
    safe_print("STARTING NVIDIA RESEMBLE.AI CHATTERBOX TTS UNIT TESTS")
    safe_print("=" * 60)
    test_audio_tts_direct()
    test_audio_tts_api_endpoint()
    safe_print("=" * 60)
    safe_print("ALL AUDIO TTS UNIT TESTS PASSED!")
    safe_print("=" * 60)

