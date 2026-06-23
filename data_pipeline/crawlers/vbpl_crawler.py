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
    # Doanh nghiệp nhỏ và vừa
    128706, 158783, 135887, 163729, 158782, 151048, 159227, 135973, 92617,
    167276, 135364, 146804, 144891, 118268, 37525, 178928, 162087, 45932,

    # Đăng ký doanh nghiệp & Hộ kinh doanh
    86507, 54879, 25963, 183843, 179097,
    136658,
    177792,

    # Quản lý thuế & Đăng ký thuế
    142619, 139896, 121188, 45750, 70289, 21397, 22623, 109859,
    159439, 186108, 174916, 66612, 83309, 97481,
    32504, 135994, 38005,
    37870,
    176827, 176829, 172686, 172687,
    27905,
    187828, 152525, 146458, 9409,

    # Hóa đơn & Chứng từ
    146169, 140495, 26308, 177581, 154800, 146457, 21889, 178309,

    # Kế toán doanh nghiệp
    113560, 26857,
    166772, 146209, 140487, 136876, 128190, 125395,
    118869, 118636, 118562, 119154, 110798,
    42740, 27757, 25792, 25714, 13039,
    144575,
    183715, 168092, 158213, 27257, 25156,

    # Lao động & Quan hệ lao động
    124207, 119205,
    152670, 43821, 174511,
    134611, 36843, 43992, 37502,
    78039,
    152668, 36142,

    # Bảo hiểm xã hội
    187119, 142815, 179965,
    186281, 181847, 180943,

    # An toàn vệ sinh lao động
    143470, 186908, 155991, 157362,
    117760,
    37475, 159197,
    135966,
    135969,

    # Sở hữu trí tuệ
    160708, 119147,
    186984, 186988, 141510,
    187492, 157722, 136041,
    164800, 164372,

    # Bảo vệ người tiêu dùng
    167086,
    141951, 186282, 181504, 179043,
    178369, 171830, 142729,
    185594, 179725, 167804,
    161263, 175419, 167051,
    152897, 143881,

    # Trọng tài thương mại
    25700, 131266,

    # Quỹ bảo lãnh tín dụng DNNVV
    128875, 139943, 133005, 37527,

    # Luật doanh nghiệp
    179095, 179941, 179942,
    152951, 142881, 142847,
    46790, 30615, 12807,

    # Luật Lao động
    139264, 146643, 70811,
    186453, 184625, 132028,

    # Bộ luật Dân sự
    95942, 96115, 46740, 171896,

    # Luật Thuế GTGT
    179382, 174917, 186981, 186979, 187347,

    # Luật Thuế TNDN
    186493, 14373,

    # Luật Thuế TNCN
    28058, 30638, 25787, 187379,
    76719, 37590, 108205
]

BASE_DIR = Path(__file__).parent.parent.parent 
OUTPUT_DIR = BASE_DIR / "data/raw/json"
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