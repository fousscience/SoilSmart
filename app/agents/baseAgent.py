from openai import OpenAI
from app.core.config import settings

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def run(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[{"role": "system", "content": self.role},
                      {"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
