import google.generativeai as genai
from app.core.config import settings

class Generator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    generator = Generator()
    answer= generator.generate("Doanh nghiệp nào phải nộp thuế thu nhập doanh nghiệp?")
    print(answer)