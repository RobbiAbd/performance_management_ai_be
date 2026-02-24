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


def _generate(prompt: str, num_predict: int = 400) -> str:
    """Panggil Ollama /api/generate. Dipakai oleh summary, motivasi, dan chatbot."""
    response = requests.post(
        settings.OLLAMA_URL,
        json={
            "model": settings.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "top_p": 0.9,
                "num_predict": num_predict,
            }
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise ValueError(f"Ollama error: {data.get('error')}")
    return (data.get("response") or "").strip()


def generate_ai_summary(prompt: str) -> str:
    return _generate(prompt, num_predict=400)


def chat_completion(messages: list[dict]) -> str:
    """
    Kirim percakapan ke Ollama /api/chat.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    Returns content dari message terakhir (assistant).
    Raises ValueError jika Ollama mengembalikan error atau content kosong.
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

    if data.get("error"):
        raise ValueError(f"Ollama error: {data.get('error')}")

    msg = data.get("message") or {}
    content = msg.get("content") or data.get("response") or ""
    content = (content or "").strip()
    if not content:
        raise ValueError(
            "Ollama returned empty content. Check model name and that Ollama is running."
        )
    return content


def _messages_to_prompt(messages: list[dict]) -> str:
    """Ubah list messages (system/user/assistant) jadi satu prompt untuk /api/generate."""
    parts = []
    for m in messages:
        role = (m.get("role") or "user").lower()
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role == "system":
            parts.append(f"Instruksi sistem:\n{content}\n")
        elif role == "user":
            parts.append(f"User: {content}\n")
        elif role == "assistant":
            parts.append(f"Asisten: {content}\n")
    parts.append("Asisten: ")
    return "\n".join(parts)


def chat_via_generate(messages: list[dict]) -> str:
    """
    Chatbot pakai /api/generate saja (sama dengan AI summary & motivasi).
    Tidak pakai /api/chat supaya konsisten dan pasti jalan kalau summary jalan.
    """
    prompt = _messages_to_prompt(messages)
    if not prompt.strip():
        raise ValueError("Prompt chat kosong")
    return _generate(prompt, num_predict=512)
