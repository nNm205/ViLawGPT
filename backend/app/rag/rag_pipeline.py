from __future__ import annotations
from app.rag.retriever import Retriever
from app.rag.prompt_builder import PromptBuilder
from app.rag.generator import Generator

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.generator = Generator()

    def ask(self, question: str) -> dict:
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            top_k=5
        )

        prompt = self.prompt_builder.build(
            question=question,
            chunks=retrieved_chunks
        )

        answer = self.generator.generate(prompt=prompt)

        return {
            "question": question,
            "answer": answer,
            "sources": retrieved_chunks
        }


if __name__ == "__main__":
    pipeline = RAGPipeline()

    question = "Doanh nghiệp tư nhân có được phát hành cổ phần không?"
    result = pipeline.ask(question)

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(
            f"- {source['metadata'].get('so_hieu')} | "
            f"{source['metadata'].get('document_title')} | "
            f"Điều {source['metadata'].get('article_number')}"
        )