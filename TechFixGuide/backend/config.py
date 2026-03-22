import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "techfix_guide")

DATABASE_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# ── App ───────────────────────────────────────────────────
APP_TITLE   = "TechFix Guide API"
APP_VERSION = "1.0.0"
DEBUG       = os.getenv("DEBUG", "true").lower() == "true"

# ── Upload ────────────────────────────────────────────────
UPLOAD_DIR  = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_MB = 10

# ── CORS ─────────────────────────────────────────────────
ALLOWED_ORIGINS = ["*"]
