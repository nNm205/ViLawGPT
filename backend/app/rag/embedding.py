impor torch 
import numpy as np 
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device="cuda" if torch.cuda.is_available() else "cpu" 
        )

    def encode_texts(
        self, 
        texts: list[str], 
        batch_size: int = 64
    ) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def encode_query(self, query: str) -> np.ndarray:
        return self.model.encode(
            query,
            normalize_embeddings=True,
        )