# ViLawGPT

Hệ thống hỏi-đáp pháp luật Việt Nam dựa trên RAG (Retrieval-Augmented Generation).  
Dữ liệu được thu thập từ [vbpl.vn](https://vbpl.vn) — cổng văn bản pháp luật quốc gia.

---

## Cấu trúc dự án

```
ViLawGPT/
├── data_pipeline/      # Thu thập, xử lý và xây dựng corpus văn bản pháp luật
└── backend/            # RAG pipeline + API server (FastAPI)
```

---

## data_pipeline

Module thu thập và chuẩn bị dữ liệu từ vbpl.vn.  
Kết quả đầu ra là file `data/articles.json` — corpus các điều luật sẵn sàng để đưa vào RAG.

### Kiến trúc

```
data_pipeline/
├── crawlers/
│   ├── vbpl_crawler.py       # Crawl HTML thô từng văn bản qua Playwright
│   ├── vbpl_processor.py     # Parse HTML → JSON chuẩn hoá (metadata + nội dung)
│   └── vbpl_catalog.py       # Tạo catalog.json — index nhẹ cho toàn bộ văn bản
├── parsers/
│   ├── article_parser.py     # Tách từng Điều từ HTML full-text
│   └── build_articles.py     # Script tạo articles.json từ toàn bộ tài liệu
├── builders/
│   └── article_corpus_builder.py  # Ghép header văn bản + nội dung điều thành corpus
├── repositories/
│   └── document_repository.py     # Load / iterate VbplDocument từ processed JSON
├── models/
│   ├── document.py           # Dataclass VbplDocument
│   └── article.py            # Dataclass Article (một Điều luật)
├── services/
│   └── catalog_service.py    # Query catalog: get / search / stats
├── utils/
│   └── logger.py             # Logger dùng chung cho toàn pipeline
├── data/
│   ├── raw/json/             # ⚠️ Không track git — HTML thô crawl về (~150 MB)
│   ├── processed/json/       # JSON chuẩn hoá sau bước processor
│   ├── catalog.json          # Index metadata toàn bộ văn bản
│   └── articles.json         # Corpus điều luật — đầu vào cho RAG
├── run_pipeline.py           # Chạy toàn bộ pipeline 4 bước
└── requirements.txt
```

### Luồng xử lý

```
vbpl.vn
   │
   ▼
[1] vbpl_crawler.py        → data/raw/json/{id}.json       (HTML thô 3 tab)
   │
   ▼
[2] vbpl_processor.py      → data/processed/json/{id}.json (metadata + content chuẩn hoá)
   │
   ▼
[3] vbpl_catalog.py        → data/catalog.json              (index nhẹ)
   │
   ▼
[4] build_articles.py      → data/articles.json             (corpus điều luật cho RAG)
```

### Cài đặt

```bash
cd data_pipeline
pip install -r requirements.txt

# Cài Playwright và Chromium (chỉ cần 1 lần)
pip install playwright
playwright install chromium
```

### Chạy từng bước

> Chạy tất cả lệnh từ thư mục `data_pipeline/`.

**Bước 1 — Crawl văn bản từ vbpl.vn**

```bash
python -m crawlers.vbpl_crawler
```

- Dùng Playwright mở trình duyệt Chromium (không headless) để crawl 3 tab của từng văn bản: `toan-van`, `thuoc-tinh`, `luoc-do`.
- Danh sách document ID cần crawl được khai báo trong `DOCUMENT_IDS` ở đầu file.
- Kết quả lưu vào `data/raw/json/{id}.json`.

> Để thêm văn bản mới, thêm ID vào danh sách `DOCUMENT_IDS` trong `crawlers/vbpl_crawler.py`.

**Bước 2 — Xử lý HTML thô**

```bash
python -m crawlers.vbpl_processor
```

- Parse HTML bằng BeautifulSoup, trích xuất metadata (số hiệu, ngày ban hành, cơ quan ban hành, ...) và đếm quan hệ văn bản (tác động / được tác động).
- Kết quả lưu vào `data/processed/json/{id}.json`.

**Bước 3 — Xây dựng catalog**

```bash
python -m crawlers.vbpl_catalog
```

- Đọc toàn bộ file trong `data/processed/json/` và tạo một file index nhẹ `data/catalog.json` để tra cứu nhanh.

**Bước 4 — Tạo corpus điều luật**

```bash
python -m parsers.build_articles
```

- Tách từng Điều từ HTML full-text dựa vào class CSS `prov-article`.
- Ghép header văn bản (số hiệu + tên) với nội dung từng Điều.
- Kết quả là `data/articles.json` — dict dạng `{doc_id}_{dieu_id} → text`.

**Chạy toàn bộ pipeline 1 lệnh**

```bash
python run_pipeline.py
```

### Văn bản đang có trong corpus

| Nhóm | Văn bản |
|------|---------|
| Luật Doanh nghiệp | Luật DN 2020 và các sửa đổi |
| Bộ luật Lao động | BLLĐ 2019 và các nghị định liên quan |
| Bộ luật Dân sự | BLDS 2015 và các sửa đổi |
| Luật Thuế GTGT | Luật 2024 và các văn bản hướng dẫn |
| Luật Thuế TNDN | Luật hiện hành |
| Luật Thuế TNCN | Luật hiện hành và các sửa đổi |
| Hỗ trợ DNNVV | Luật hỗ trợ doanh nghiệp nhỏ và vừa |

### Lưu ý

- `data/raw/json/` **không được track trên git** vì quá nặng (~150 MB). Cần chạy lại bước 1 để tái tạo.
- Log được ghi vào `crawler.log` và `catalog.log` trong thư mục `data_pipeline/`.
- Nếu một document bị lỗi khi crawl, pipeline sẽ log exception và tiếp tục các document còn lại — không dừng toàn bộ.

---

## backend

*(Tài liệu đang cập nhật)*
