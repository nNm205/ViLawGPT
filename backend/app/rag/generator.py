from __future__ import annotations
from openai import OpenAI
from app.core.config import settings

class Generator:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key="local-llm"
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": user_prompt }
            ],
            max_tokens=512,
            temperature=0.1,
            top_p=0.9
        )

        return response.choices[0].message.content.strip()