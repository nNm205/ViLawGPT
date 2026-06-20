from __future__ import annotations
import re 
import json
import logging 
from pathlib import Path
from bs4 import BeautifulSoup
from unidecode import unidecode
from datetime import datetime 

######################################################
# CONSTANTS
######################################################

BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "data/processed/json"
OUTPUT_FILE = BASE_DIR / "data/catalog.json"

######################################################
# LOGGING
######################################################

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            "catalog.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

######################################################
# BUILD CATALOG 
######################################################

def build_catalog(processed_doc: dict) -> dict:
    document_id = processed_doc["doc_id"]
    logger.info("Building catalog %s", document_id)

    catalog = {
        "id": document_id,
        "url_chi_tiet": processed_doc["thuoc_tinh"]["url_chi_tiet"],
        "content_length": processed_doc["noi_dung"]["content_length"],
        "ten_van_ban": processed_doc["thuoc_tinh"]["ten_van_ban"],
        "so_hieu": processed_doc["thuoc_tinh"]["so_hieu"],
        "loai_van_ban": processed_doc["thuoc_tinh"]["loai_van_ban"],
        "ngay_ban_hanh": processed_doc["thuoc_tinh"]["ngay_ban_hanh"],
        "trang_thai_hieu_luc": processed_doc["thuoc_tinh"]["trang_thai_hieu_luc"],
        "co_quan_ban_hanh": processed_doc["thuoc_tinh"]["co_quan_ban_hanh"],
        "van_ban_tac_dong_count": processed_doc["thuoc_tinh"]["van_ban_tac_dong_count"],
        "van_ban_duoc_tac_dong_count": processed_doc["thuoc_tinh"]["van_ban_duoc_tac_dong_count"]
    }    

    logger.info("Finished catalog %s", document_id)
    return catalog

######################################################
# MAIN 
######################################################

def main():
    catalogs = []
    files = list(INPUT_DIR.glob("*.json"))
    logger.info("Found %s documents", len(files))

    for idx, file in enumerate(files, start=1):
        logger.info("[%s/%s] Processing %s", idx, len(files), file.name)

        with open(file, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)
        
        try:
            catalog = build_catalog(raw_doc)
            catalogs.append(catalog) 
        except Exception as e:
            logger.exception("Error processing %s", file.name) 

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalogs, f, ensure_ascii=False, indent=2) 
    
    logger.info("Saved %s catalogs -> %s", len(catalogs), OUTPUT_FILE)

if __name__ == "__main__":
    main()