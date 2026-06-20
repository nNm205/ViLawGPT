import chromadb 
from app.core.config import settings
from embedding import EmbeddingModel

class Retriever:
    def __init__(self):
        self.model = EmbeddingModel()
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_collection(settings.CHROMA_COLLECTION_NAME)

    def retrieve(self, query: str, top_k: int = 5):
        query_embedding = self.model.encode_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )
        return results 

if __name__ == "__main__":
    retriever = Retriever()
    results = retriever.retrieve(
        "Doanh nghiệp nào phải nộp thuế thu nhập doanh nghiệp?"
    )
    print(results)