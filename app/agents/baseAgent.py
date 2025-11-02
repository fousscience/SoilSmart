from openai import OpenAI
from app.core.config import settings

# Singleton OpenAI client to reuse connections
_openai_client = None

def get_openai_client():
    """Get or create OpenAI client instance (singleton)"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = get_openai_client()  # Reuse shared client

    def run(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[{"role": "system", "content": self.role},
                      {"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
