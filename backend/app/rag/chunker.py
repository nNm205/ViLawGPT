from __future__ import annotations
import json
import logging
from pathlib import Path
from app.core.logger import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =====================================================
# CONSTANTS
# =====================================================

MAX_CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).parent.parent.parent.parent
ARTICLES_FILE = BASE_DIR / "data/articles.json"
CATALOG_FILE = BASE_DIR / "data/catalog.json"
OUTPUT_FILE = BASE_DIR / "data/processed/chunks.json"

# =====================================================
# LOGGING
# =====================================================

logger = setup_logger(__name__)

# =====================================================
# SPLITTER
# =====================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=MAX_CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", "; ", " "]
)

# =====================================================
# HELPERS
# =====================================================

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_catalog_lookup(catalog: list[dict]) -> dict:
    lookup = {}

    for doc in catalog:
        doc_id = str(doc["id"])
        lookup[doc_id] = {
            "document_title": doc.get("ten_van_ban"),
            "so_hieu": doc.get("so_hieu"),
            "loai_van_ban": doc.get("loai_van_ban"),
            "co_quan_ban_hanh": doc.get("co_quan_ban_hanh"),
            "ngay_ban_hanh": doc.get("ngay_ban_hanh"),
            "trang_thai_hieu_luc": doc.get("trang_thai_hieu_luc"),
            "url_chi_tiet": doc.get("url_chi_tiet"),
        }

    return lookup

def parse_article_key(key: str):
    parts = key.rsplit("_")

    if len(parts) == 3:
        document_id, article_number, clause_number = parts 
        return {
            "document_id": document_id,
            "article_number": int(article_number),
            "clause_number": int(clause_number),
            "point_number": None 
        }

    if len(parts) == 4:
        document_id, article_number, clause_number, point_number = parts 
        return {
            "document_id": document_id,
            "article_number": int(article_number),
            "clause_number": int(clause_number),
            "point_number": point_number 
        }

    raise ValueError(f"Invalid key: {key}")

def split_text(text: str) -> list[str]:
    if len(text) <= MAX_CHUNK_SIZE:
        return [text]
    
    return splitter.split_text(text)

# =====================================================
# CHUNKING
# =====================================================

def build_chunks(
    articles: dict,
    catalog_lookup: dict
) -> list[dict]:
    chunks = []
    total_missing_docs = 0
    total_split_chunks = 0

    for article_key, article_text in articles.items():
        try:
            parsed = parse_article_key(article_key)
        except Exception:
            logger.warning(f"Cannot parse key: {article_key}")
            continue

        document_id = parsed["document_id"]
        metadata = catalog_lookup.get(document_id)
        if metadata is None:
            total_missing_docs += 1
            logger.warning(f"Document metadata not found: {document_id}")
            continue

        text_parts = split_text(article_text)
        if len(text_parts) > 1:
            total_split_chunks += 1

        for idx, text_part in enumerate(text_parts):
            chunk_id = article_key

            if len(text_part) > 1:
                chunk_id = f"{article_key}_{idx}"

            chunk = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": metadata["document_title"],
                "article_number": parsed["article_number"],
                "clause_number": parsed["clause_number"],
                "point_number": parsed["point_number"],   
                "text": text_part,
                "metadata": {
                    "so_hieu": metadata["so_hieu"],
                    "loai_van_ban": metadata["loai_van_ban"],
                    "co_quan_ban_hanh": metadata["co_quan_ban_hanh"],
                    "ngay_ban_hanh": metadata["ngay_ban_hanh"],
                    "trang_thai_hieu_luc": metadata["trang_thai_hieu_luc"],
                    "url_chi_tiet": metadata["url_chi_tiet"],
                }
            }

            chunks.append(chunk)

    logger.info(f"Total chunks: {len(chunks)}")
    logger.info(f"Missing documents: {total_missing_docs}")
    logger.info(f"Split chunks: {total_split_chunks}")

    return chunks


# =====================================================
# SAVE
# =====================================================

def save_chunks(chunks: list[dict]):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(chunks)} chunks -> {OUTPUT_FILE}")

# =====================================================
# MAIN
# =====================================================

def main():
    logger.info("Loading articles...")
    articles = load_json(ARTICLES_FILE)

    logger.info("Loading catalog...")
    catalog = load_json(CATALOG_FILE)
    
    catalog_lookup = build_catalog_lookup(catalog)
    
    logger.info("Building chunks...")
    chunks = build_chunks(
        articles=articles, 
        catalog_lookup=catalog_lookup
    )
    
    save_chunks(chunks)
    logger.info("Done")

if __name__ == "__main__":
    main()