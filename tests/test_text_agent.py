import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.agents.text_agent import text_agent

client = TestClient(app)

def safe_print(text: str):
    """Safely print text handling Windows cp1252 stdout limitations."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def test_health_endpoint():
    """Verify health endpoint responds with 200 and correct status."""
    safe_print("\n[TEST 1] Testing /api/v1/health...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agents"]["text"] == "online"
    safe_print("[PASS] Health check endpoint passed.")

def test_text_agent_direct():
    """Verify TextAgent class directly processes input and produces meaningful responses."""
    safe_print("\n[TEST 2] Testing TextAgent process() method directly...")
    result = text_agent.process(
        user_message="Say 'OmniAgent Text AI is online' and nothing else.",
        temperature=0.2,
        max_tokens=150
    )
    assert "response" in result
    assert len(result["response"]) > 0, "Response must not be empty"
    assert result["agent_name"] == "Text AI Agent"
    safe_print(f"[PASS] TextAgent direct output: {repr(result['response'].strip())}")

def test_text_chat_api_endpoint():
    """Verify the /api/v1/chat/text FastAPI route with payload validation."""
    safe_print("\n[TEST 3] Testing /api/v1/chat/text HTTP POST endpoint...")
    payload = {
        "message": "What are 3 key advantages of a multi-agent AI system over a single agent?",
        "history": [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hello! I am your Text AI Agent."}
        ],
        "temperature": 0.5,
        "max_tokens": 300
    }
    response = client.post("/api/v1/chat/text", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    body = response.json()
    assert "response" in body
    assert body["agent_name"] == "Text AI Agent"
    assert len(body["response"]) > 20
    safe_print("[PASS] /api/v1/chat/text endpoint returned valid response:")
    safe_print("--------------------------------------------------")
    safe_print(body["response"][:200] + "...")
    safe_print("--------------------------------------------------")

if __name__ == "__main__":
    safe_print("Starting Comprehensive Text AI Unit Tests...")
    test_health_endpoint()
    test_text_agent_direct()
    test_text_chat_api_endpoint()
    safe_print("\nALL TEXT AI UNIT TESTS PASSED SUCCESSFULLY! [OK]")
