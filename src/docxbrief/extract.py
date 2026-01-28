from __future__ import annotations

from pathlib import Path
from docx import Document
from .config import Config


def extract_docx_text(cfg: Config, path: Path) -> str:
    doc = Document(str(path))
    parts: list[str] = []
    for para in doc.paragraphs:
        t = (para.text or "").strip()
        if not t:
            continue
        parts.append(t)
    text = "\n".join(parts)
    max_chars = int(cfg.raw.get("extract", {}).get("max_chars_per_file", 12000))
    return text[:max_chars]
