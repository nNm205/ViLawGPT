from __future__ import annotations
from app.rag.retriever import Retriever
from app.rag.prompt_builder import PromptBuilder
from app.rag.generator import Generator
from app.rag.citation_builder import CitationBuilder

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.generator = Generator()
        self.citation_builder = CitationBuilder()

    def ask(self, question_id: int, question: str) -> dict:
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            top_k=5
        )

        system_prompt, user_prompt = self.prompt_builder.build(
            question=question,
            chunks=retrieved_chunks
        )

        answer = self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        relevant_docs, relevant_articles = self.citation_builder.build(
            retrieved_chunks
        )

        return {
            "id": question_id,
            "question": question,
            "answer": answer,
            "relevant_docs": relevant_docs,
            "relevant_articles": relevant_articles
        }


if __name__ == "__main__":
    pipeline = RAGPipeline()
    
    result = pipeline.ask(
        question_id=2,
        question="Doanh nghiệp nhỏ và vừa phải đáp ứng điều kiện nào để được hỗ trợ theo Luật Hỗ trợ doanh nghiệp nhỏ và vừa?"
    )

    print(result)