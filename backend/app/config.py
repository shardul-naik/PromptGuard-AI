from pathlib import Path
import os

from dotenv import load_dotenv


# Project root:
# PromptGuard-AI/
ROOT_DIR = Path(__file__).resolve().parents[2]

ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
CACHE_RESPONSE_FILE = DATA_DIR / "cache_responses.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# OpenAI
# -----------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        f"OPENAI_API_KEY was not found in {ENV_PATH}. "
        "Make sure your .env file exists in the project root."
    )

LOW_MODEL = os.getenv("LOW_MODEL", "gpt-5.4-nano")
MEDIUM_MODEL = os.getenv("MEDIUM_MODEL", "gpt-5.4-mini")
HIGH_MODEL = os.getenv("HIGH_MODEL", "gpt-5.4")

ANALYZER_MODEL = os.getenv("ANALYZER_MODEL", "gpt-5.4-nano")
MODERATION_MODEL = os.getenv(
    "MODERATION_MODEL",
    "omni-moderation-latest",
)


# -----------------------------
# Routing
# -----------------------------

LOW_THRESHOLD = float(os.getenv("LOW_THRESHOLD", "3.5"))
HIGH_THRESHOLD = float(os.getenv("HIGH_THRESHOLD", "7.0"))


# -----------------------------
# Semantic cache
# -----------------------------

CACHE_SIMILARITY_THRESHOLD = float(
    os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.90")
)


# -----------------------------
# Request limits
# -----------------------------

MAX_CONTENT_CHARS = int(
    os.getenv("MAX_CONTENT_CHARS", "120000")
)

MAX_OUTPUT_TOKENS = int(
    os.getenv("MAX_OUTPUT_TOKENS", "1200")
)


# -----------------------------
# Frontend
# -----------------------------

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)