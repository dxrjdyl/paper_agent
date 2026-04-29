from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
POSTER_DIR = DATA_DIR / "posters"
EXPORT_DIR = DATA_DIR / "exports"
CHROMA_DIR = DATA_DIR / "chroma"
DB_PATH = DATA_DIR / "library.sqlite3"

for p in [DATA_DIR, PDF_DIR, POSTER_DIR, EXPORT_DIR, CHROMA_DIR]:
    p.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

APP_TITLE = "Graduate Multi-Agent Literature System"
