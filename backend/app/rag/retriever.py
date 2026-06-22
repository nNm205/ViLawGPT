import chromadb 
from app.core.config import settings
from app.rag.embedding import EmbeddingModel

class Retriever:
    MIN_SCORE = 0.30

    def __init__(self):
        self.model = EmbeddingModel()
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_collection(settings.CHROMA_COLLECTION_NAME)

    def retrieve(
        self, 
        query: str, 
        top_k: int = 5
    ):
        query_embedding = self.model.encode_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        retrieved_chunks = []
        for i in range(len(results["ids"][0])):
            score = 1 - results["distances"][0][i]
            if score < self.MIN_SCORE:
                continue

            retrieved_chunks.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "score": score,
                "metadata": results["metadatas"][0][i]
            })

        retrieved_chunks.sort(key=lambda x: x["score"], reverse=True)
        return retrieved_chunks