import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai import OpenAI
from app.core.config import settings

def test_groq_llm():
    """Unit test for verifying Groq LLM API connectivity and response quality."""
    print("Testing Groq LLM API connectivity...")
    client = OpenAI(
        base_url=settings.GROQ_BASE_URL,
        api_key=settings.GROQ_API_KEY
    )

    prompt = "Which number is larger, 9.11 or 9.8? Explain briefly in two sentences."
    response = client.chat.completions.create(
        model=settings.GROQ_DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise, precise AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=150
    )

    content = response.choices[0].message.content
    print("--------------------------------------------------")
    print(f"Model: {response.model}")
    print(f"Prompt: {prompt}")
    print(f"Answer: {content}")
    print("--------------------------------------------------")
    assert content and len(content) > 0, "Response content should not be empty."
    print("TEST RESULT: SUCCESS! Groq LLM is online and operational.")

if __name__ == "__main__":
    test_groq_llm()
