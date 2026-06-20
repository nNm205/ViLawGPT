from __future__ import annotations
import json
import logging
from pathlib import Path

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).parent.parent.parent.parent
ARTICLES_FILE = BASE_DIR / "data/articles.json"
CATALOG_FILE = BASE_DIR / "data/catalog.json"
OUTPUT_FILE = BASE_DIR / "data/processed/chunks.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

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

def parse_article_key(key: str) -> tuple[str, int]:
    document_id, article_number = key.rsplit("_", 1)
    return document_id, int(article_number)

# =====================================================
# CHUNKING
# =====================================================

def build_chunks(
    articles: dict,
    catalog_lookup: dict
) -> list[dict]:
    chunks = []
    total_missing_docs = 0

    for article_key, article_text in articles.items():
        try:
            document_id, article_number = parse_article_key(article_key)
        except Exception:
            logger.warning(f"Cannot parse article key: {article_key}")
            continue

        metadata = catalog_lookup.get(document_id)
        if metadata is None:
            total_missing_docs += 1
            logger.warning(f"Document metadata not found: {document_id}")
            continue

        chunk = {
            "chunk_id": article_key,
            "document_id": document_id,
            "document_title": metadata["document_title"],
            "article_number": article_number,
            "text": article_text,
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
    chunks = build_chunks(articles=articles, catalog_lookup=catalog_lookup)
    save_chunks(chunks)
    logger.info("Done")

if __name__ == "__main__":
    main()