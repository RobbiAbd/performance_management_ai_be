import requests
from app.core.config import settings

def _ollama_chat_url():
    """Base URL untuk Ollama API chat (POST /api/chat)."""
    base = (settings.OLLAMA_URL or "").rstrip("/")
    if base.endswith("/generate"):
        return base[:-9] + "/chat"
    if "/api/generate" in base:
        return base.replace("/api/generate", "/api/chat")
    return (base or "http://localhost:11434") + "/api/chat"


def generate_ai_summary(prompt: str):
    response = requests.post(
        settings.OLLAMA_URL,
        json={
            "model": settings.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "top_p": 0.9,
                "num_predict": 400
            }
        }
    )

    return response.json()["response"]


def chat_completion(messages: list[dict]) -> str:
    """
    Kirim percakapan ke Ollama /api/chat.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    Returns content dari message terakhir (assistant).
    """
    url = _ollama_chat_url()
    response = requests.post(
        url,
        json={
            "model": settings.MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "top_p": 0.9,
                "num_predict": 512,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    msg = data.get("message") or {}
    return (msg.get("content") or "").strip()
