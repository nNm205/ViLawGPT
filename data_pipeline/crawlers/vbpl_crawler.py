from __future__ import annotations
import json 
import logging
import time
from pathlib import Path 
from playwright.sync_api import (
    Page,
    sync_playwright
)

######################################################
# CONSTANTS
######################################################

DOCUMENT_IDS = [
    # Luật doanh nghiệp
    179095, 179941, 179942, 152951, 142881, 142847, 128706, 46790, 30615, 12807,

    # Luật Lao động
    139264, 146643, 70811, 186453, 184625, 152668, 132028,

    # Bộ luật Dân sự
    95942, 96115, 46740, 171896,

    # Luật Thuế GTGT
    179382, 174917, 186981, 186979, 187347,

    # Luật Thuế TNDN
    186493, 14373,

    # Luật Thuế TNCN
    28058, 30638, 25787, 187379, 76719, 37590, 108205,

    # Luật Hỗ trợ doanh nghiệp nhỏ và vừa
    158783, 158782
]

OUTPUT_DIR = Path("data/raw/json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PAGE_TIMEOUT = 30_000
TAB_WAIT_MS = 2_000

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

def build_url(document_id: int) -> str:
    return f"https://vbpl.vn/van-ban/chi-tiet/--{document_id}" 

def extract_document_id(url: str) -> str:
    return url.split("--")[-1]

def save_json(document_id: str, data: dict):
    output_file = OUTPUT_DIR / f"{document_id}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("Saved document %s -> %s", document_id, output_file)

######################################################
# CRAWLERS
######################################################

def crawl_tab(page: Page, url: str, tab: str) -> str:
    tab_url = f"{url}?tabs={tab}"

    logger.info("Loading tab %s,", tab)

    page.goto(tab_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)

    if tab == "toan-van":
        page.wait_for_selector("text=CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", timeout=PAGE_TIMEOUT)
    else:
        page.wait_for_timeout(TAB_WAIT_MS)

    return page.locator("body").inner_html()

def crawl_document(page: Page, url: str) -> dict:
    start_time = time.perf_counter()
    document_id = extract_document_id(url)

    logger.info("Start crawl: %s", url)

    result = {
        "document_id": document_id,
        "url": url,
        "crawl_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "toan_van_html": crawl_tab(page, url, "toan-van"),
        "thuoc_tinh_html": crawl_tab(page, url, "thuoc-tinh"),
        "luoc_do_html": crawl_tab(page, url, "luoc-do"),
    }

    result["crawl_time_seconds"] = round(time.perf_counter() - start_time, 2)

    logger.info("Finished crawl %s in %.2fs", document_id, result["crawl_time_seconds"])
    return result 

######################################################
# MAIN
######################################################

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)

        for doc_id in DOCUMENT_IDS:
            page = context.new_page()

            try:
                url = build_url(doc_id)
                result = crawl_document(page, url)
                save_json(result["document_id"], result)
            except Exception as e:
                logger.exception("Failed crawl %s", url)
            finally:
                page.close()

        browser.close()

if __name__ == "__main__":
    main()