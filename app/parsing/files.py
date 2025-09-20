import io
import re
from typing import Tuple
import pdfplumber
import docx2txt
import tempfile


def _normalize(text: str) -> str:
    # Basic normalization: strip, collapse whitespace, remove excessive headers/footers hints
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_pdf_bytes(data: bytes) -> str:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            try:
                out.append(page.extract_text() or "")
            except Exception:
                continue
    return _normalize("\n".join(out))


def extract_text_from_docx_bytes(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
        tmp.write(data)
        tmp.flush()
        text = docx2txt.process(tmp.name) or ""
    return _normalize(text)


def extract_text(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Returns (text, ext)
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf_bytes(file_bytes), "pdf"
    if name.endswith(".docx"):
        return extract_text_from_docx_bytes(file_bytes), "docx"
    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")
