from app.rag.retriever import Retriever
from app.rag.prompt_builder import PromptBuilder
from app.rag.generator import Generator

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.generator = Generator()

    def ask(self, question: str) -> str:
        chunks = self.retriever.retrieve(question)
        prompt = self.prompt_builder.build(question, chunks)
        answer = self.generator.generate(prompt)
        return answer
    
if __name__ == "__main__":
    pipeline = RAGPipeline()

    question = """
    Doanh nghiệp tư nhân có được phát hành cổ phần không?
    """

    answer = pipeline.ask(question)
    print(answer)