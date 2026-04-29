from pathlib import Path
import re
import shutil
import uuid
import pymupdf
from config import PDF_DIR

class PDFService:
    def save_uploaded_pdf(self, uploaded_file) -> Path:
        safe_name = re.sub(r"[^\w\-.\u4e00-\u9fa5]", "_", uploaded_file.name)
        dest = PDF_DIR / f"{uuid.uuid4().hex[:8]}_{safe_name}"
        with open(dest, "wb") as f:
            shutil.copyfileobj(uploaded_file, f)
        return dest

    def extract_text(self, pdf_path: str | Path) -> str:
        doc = pymupdf.open(str(pdf_path))
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append(f"\n\n--- Page {i+1} ---\n{text}")
        return "\n".join(pages).strip()

    def extract_metadata(self, pdf_path: str | Path) -> dict:
        doc = pymupdf.open(str(pdf_path))
        meta = doc.metadata or {}
        return {
            "title": meta.get("title") or Path(pdf_path).stem,
            "author": meta.get("author") or "",
            "pages": len(doc),
            "path": str(pdf_path),
        }
