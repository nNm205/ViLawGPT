from __future__ import annotations
import google.generativeai as genai
from app.core.config import settings
class Generator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=settings.LLM_MODEL)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()