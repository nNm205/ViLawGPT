import json
import chromadb 
from pathlib import Path 
from tqdm import tqdm
from app.core.config import settings
from app.core.logger import setup_logger
from app.rag.embedding import EmbeddingModel

# =====================================================
# LOGGING
# =====================================================

logger = setup_logger(__name__)

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).parent.parent.parent.parent
CHUNKS_FILE = BASE_DIR / "data/processed/chunks.json"
BATCH_SIZE = 128

# =====================================================
# MAIN
# =====================================================

def main():
    try:
        # =====================================================
        # Load chunks
        # =====================================================

        logger.info("Loading chunks from %s", CHUNKS_FILE)
        
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        logger.info("Loaded %s chunks", len(chunks))

        # =====================================================
        # Embedding model
        # =====================================================

        logger.info("Loading embedding model...")

        model = EmbeddingModel()

        logger.info("Embedding model loaded successfully")
        
        # =====================================================
        # ChromaDB
        # =====================================================

        logger.info(
            "Connecting to ChromaDB at %s", 
            settings.CHROMA_DB_PATH
        )

        client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )

        try:
            client.delete_collection(
                settings.CHROMA_COLLECTION_NAME
            )
            
            logger.info(
                "Deleted existing collection %s", 
                settings.CHROMA_COLLECTION_NAME
            )
        except Exception:
            logger.info(
                "Collection '%s' does not exist", 
                settings.CHROMA_COLLECTION_NAME
            ) 

        collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )

        logger.info(
            "Created collection '%s'", 
            settings.CHROMA_COLLECTION_NAME
        )

        # =====================================================
        # Building index 
        # =====================================================

        logger.info(
            "Building vector index with batch size = %s", 
            BATCH_SIZE
        )

        for i in tqdm(
            range(0, len(chunks), BATCH_SIZE), 
            desc="Building Chroma Index"
        ):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            texts = [chunk["text"] for chunk in batch_chunks]
            embeddings = model.encode_texts(texts)
            ids = [chunk["chunk_id"] for chunk in batch_chunks]
            documents = texts
            metadatas = [
                {
                    "document_id": str(chunk.get("document_id") or ""),
                    "document_title": str(chunk.get("document_title") or ""),
                    "article_number": int(chunk.get("article_number") or 0),
                    "clause_number": int(chunk.get("clause_number") or 0),
                    "point_number": str(chunk.get("point_number") or ""),
                    "so_hieu": str(chunk["metadata"].get("so_hieu") or ""),
                    "loai_van_ban": str(chunk["metadata"].get("loai_van_ban") or ""),
                    "co_quan_ban_hanh": str(chunk["metadata"].get("co_quan_ban_hanh") or ""),
                    "trang_thai_hieu_luc": str(chunk["metadata"].get("trang_thai_hieu_luc") or ""),
                    "chunk_length": len(chunk["text"])
                } 
                for chunk in batch_chunks
            ]

            collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas
            )

            inserted = min(i + BATCH_SIZE, len(chunks))
            logger.info(f"Inserted %s/%s chunks", inserted, len(chunks))

        logger.info("Index build completed successfully")
    except Exception:
        logger.exception("Failed to build vector index")
        raise

if __name__ == "__main__":
    main()