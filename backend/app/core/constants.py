# =========================
# Chunking
# =========================

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100

# =========================
# Retrieval
# =========================

DEFAULT_TOP_K = 5

# =========================
# Supported file types
# =========================

SUPPORTED_DOCUMENT_EXTENSIONS = [
    ".pdf", "doc", ".docx"
]

# =========================
# Environment
# =========================

ENV_DEVELOPMENT = "development"
ENV_PRODUCTION = "production"

# =========================
# Logging
# =========================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)