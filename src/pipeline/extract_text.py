from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import fitz  # PyMuPDF


def extract_text_and_metadata(path: Path) -> Tuple[str, Dict]:
    """
    Extract text + PDF metadata using PyMuPDF.
    For .txt files, read text and return basic metadata.
    """
    ext = path.suffix.lower()

    if ext == ".txt":
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta = {
            "title": path.name,
            "author": None,
            "created_date": None,
            "page_count": None,
        }
        return text, meta

    if ext == ".pdf":
        doc = fitz.open(str(path))
        meta_raw = doc.metadata or {}

        parts = []
        for page in doc:
            parts.append(page.get_text("text"))

        text = "\n".join(parts).strip()

        meta = {
            "title": meta_raw.get("title") or path.name,
            "author": meta_raw.get("author"),
            "created_date": meta_raw.get("creationDate") or meta_raw.get("created"),
            "page_count": doc.page_count,
        }
        doc.close()
        return text, meta

    raise ValueError(f"Unsupported file type for extraction: {ext}")