from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # =========================
    # Base Paths
    # =========================
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"                 # backend/data
    RAW_DATA_DIR = DATA_DIR / "raw"              # backend/data/raw
    PROCESSED_DATA_DIR = DATA_DIR / "processed"  # backend/data/processed
    VECTOR_STORE_DIR = DATA_DIR / "vector_store" # backend/data/vector_store
    EMBEDDINGS_DIR = DATA_DIR / "embeddings"     # backend/data/embeddings

    # =========================
    # Environment
    # =========================
    ENV: str = "development"
    DEBUG: bool = True

    # =========================
    # Gemini
    # =========================
    GOOGLE_API_KEY: str

    # =========================
    # Models
    # =========================
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    LLM_MODEL: str = "gemini-2.5-flash"

    # =========================
    # Retrieval
    # =========================
    TOP_K: int = 5

    # =========================
    # Chunking
    # =========================
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # =========================
    # Chroma
    # =========================
    CHROMA_COLLECTION_NAME: str = "vilawgpt"
    CHROMA_DB_PATH: str = "data/vector_store/chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()