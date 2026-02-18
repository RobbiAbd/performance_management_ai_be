import requests
from app.core.config import settings

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
