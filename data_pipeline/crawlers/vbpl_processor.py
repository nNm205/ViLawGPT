from __future__ import annotations
import re 
import json 
import logging
from datetime import datetime 
from pathlib import Path
from bs4 import BeautifulSoup

######################################################
# PATHS
######################################################

INPUT_DIR = Path("data/raw/json")
OUTPUT_DIR = Path("data/processed/json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

######################################################
# CONSTANTS
######################################################

METADATA_FIELDS_MAP = {
    "số hiệu": "so_hieu",
    "tên văn bản": "ten_van_ban",
    "loại văn bản": "loai_van_ban",
    "loại code": "loai_code",
    "ngày ban hành": "ngay_ban_hanh",
    "ngày có hiệu lực": "hieu_luc_tu",
    "ngày hết hiệu lực": "hieu_luc_den",
    "tình trạng hiệu lực": "trang_thai_hieu_luc",
    "trạng thái code": "trang_thai_code",
    "cơ quan ban hành": "co_quan_ban_hanh",
    "ngành": "bo_nganh",
    "ngôn ngữ": "ngon_ngu",
    "lượt xem": "luot_xem",
    "ngày cập nhật": "ngay_cap_nhat",
    "trạng thái xuất bản": "trang_thai_xuat_ban",
    "nội dung": "noi_dung",
    "thuộc tính": "thuoc_tinh",
    "lược đồ": "luoc_do",
    "lịch sử": "lich_su",
    "lĩnh vực": "linh_vuc",
    "chức danh": "chuc_danh",
    "người ký": "nguoi_ky"
}

TAC_DONG = {
    "Văn bản hướng dẫn áp dụng",
    "Văn bản quy định chi tiết, hướng dẫn thi hành",
    "Văn bản hợp nhất",
    "Văn bản sửa đổi bổ sung",
    "Văn bản đính chính",
    "Văn bản thay thế",
    "Văn bản bãi bỏ",
    "Văn bản dẫn chiếu",
    "Văn bản áp dụng",
    "Văn bản giải thích",
    "Văn bản đình chỉ thi hành",
    "Văn bản tạm ngưng hiệu lực",
    "Văn bản công bố"
}

DUOC_TAC_DONG = {
    "Văn bản được hướng dẫn áp dụng", 
    "Văn bản được quy định chi tiết, hướng dẫn thi hành",
    "Văn bản được hợp nhất", 
    "Văn bản được sửa đổi bổ sung",
    "Văn bản được đính chính", 
    "Văn bản được thay thế",
    "Văn bản bị bãi bỏ",
    "Văn bản được dẫn chiếu",
    "Căn cứ ban hành",
    "Văn bản được giải thích",
    "Văn bản bị đình chỉ thi hành",
    "Văn bản bị tạm ngưng hiệu lực",
    "Văn bản được công bố",
}

######################################################
# LOGGING
######################################################

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("crawler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

######################################################
# HELPERS
######################################################

def normalize_date(date_str: str) -> str | None:
    if not date_str:
        return None 

    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None

def get_code(text: str) -> str:
    if not text:
        return None 
    
    return "".join(word[0].upper() for word in text.split())

######################################################
# EXTRACTIONS 
######################################################

def extract_title(toan_van_html: str) -> str | None:
    soup = BeautifulSoup(toan_van_html, "lxml")
    title = soup.find("h1", class_="lawDocumentHeader_title___34g0")
    
    if not title:
        logger.warning("Cannot find title")
        return None 

    return title.get_text(" ", strip=True)

def extract_metadata(thuoc_tinh_html: str) -> dict:
    soup = BeautifulSoup(thuoc_tinh_html, "lxml")
    metadata = {}
    containers = soup.find_all("div", class_="ant-descriptions-item-container")

    for container in containers:
        label = container.find("span", class_="ant-descriptions-item-label")
        content = container.find("span", class_="ant-descriptions-item-content")

        if not label or not content:
            continue 

        label_text = label.get_text(strip=True).lower()

        key = METADATA_FIELDS_MAP.get(label_text)
        if not key:
            continue 

        value = content.get_text(" ", strip=True)

        if key in {"ngay_ban_hanh", "hieu_luc_tu", "hieu_luc_den"}:
            value = normalize_date(value)
        
        metadata[key] = value

    logger.debug("Extracted %s metadata fields", len(metadata))
    return metadata

def extract_relation_counts(luoc_do_html: str) -> tuple[int, int]:
    soup = BeautifulSoup(luoc_do_html, "lxml")
    tac_dong_count = 0
    duoc_tac_dong_count = 0

    for span in soup.find_all("span"):
        text = span.get_text(" ", strip=True)

        match = re.match(r"(.+?)\s*\((\d+)\)", text)
        if not match:
            continue

        relation_name = match.group(1).strip()
        count = int(match.group(2))

        if relation_name in TAC_DONG: 
            tac_dong_count += count
        elif relation_name in DUOC_TAC_DONG: 
            duoc_tac_dong_count += count
    
    logger.debug("Relations: tac_dong=%s, duoc_tac_dong=%s", tac_dong_count, duoc_tac_dong_count)
    return tac_dong_count, duoc_tac_dong_count

######################################################
# BUILD DOCUMENT
######################################################

def build_document(raw_doc: dict) -> dict:
    metadata = extract_metadata(raw_doc["thuoc_tinh_html"])
    tac_dong_count, duoc_tac_dong_count = extract_relation_counts(raw_doc["luoc_do_html"])

    document = {}
    document["doc_id"] = raw_doc["document_id"] 
    document["thuoc_tinh"] = {
        "id": raw_doc["document_id"],
        "so_hieu": metadata.get("so_hieu"),
        "ten_van_ban": extract_title(raw_doc["toan_van_html"]),
        "loai_van_ban": metadata.get("loai_van_ban"),
        "loai_code": get_code(metadata.get("loai_van_ban")),
        "ngay_ban_hanh": metadata.get("ngay_ban_hanh"),
        "hieu_luc_tu": metadata.get("hieu_luc_tu"),
        "hieu_luc_den": metadata.get("hieu_luc_den"),
        "trang_thai_hieu_luc": metadata.get("trang_thai_hieu_luc"),
        "trang_thai_code": get_code(metadata.get("trang_thai_hieu_luc")),
        "co_quan_ban_hanh": metadata.get("co_quan_ban_hanh"),
        "bo_nganh": metadata.get("bo_nganh"),
        "url_chi_tiet": raw_doc["url"],
        "van_ban_tac_dong_count": tac_dong_count,
        "van_ban_duoc_tac_dong_count": duoc_tac_dong_count
    }
    document["noi_dung"] = {
        "id": raw_doc["document_id"],
        "content_html": raw_doc["toan_van_html"],
        "content_length": len(raw_doc["toan_van_html"])
    }
    document["crawl_time_seconds"] = raw_doc["crawl_time_seconds"]
    document["crawled_at"] = raw_doc["crawl_at"]

    return document 

######################################################
# MAIN
######################################################

def main():
    files = list(INPUT_DIR.glob("*.json"))
    logger.info("Found %s documents", len(files))

    for idx, file in enumerate(files, start=1):
        logger.info("[%s/%s] Processing %s", idx, len(files), file.name)

        with open(file, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)

        try:
            processed_doc = build_document(raw_doc)
            output_path = OUTPUT_DIR / file.name

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(processed_doc, f, ensure_ascii=False, indent=2)

            logger.info("Updated %s", file.name)

        except Exception as e:
            logger.exception("Error processing %s", file.name) 

if __name__ == "__main__":
    main()