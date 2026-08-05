"""Resume text parser — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Extracts plain text from PDF, DOCX, or raw .txt inputs.
Falls back gracefully when optional dependencies are unavailable.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger("component1.parser")


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Extract plain text from uploaded file bytes.

    Parameters
    ----------
    data:     Raw file bytes.
    filename: Original filename (used to detect extension).

    Returns
    -------
    Extracted text string (may be empty if the file has no readable text).
    """
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _from_pdf(data)
    elif suffix == ".docx":
        return _from_docx(data)
    else:
        # Assume plain text; handle BOM and encoding gracefully
        return _from_text_bytes(data)


def extract_text_from_path(path: Union[str, Path]) -> str:
    """Read and extract text from a local file path."""
    path = Path(path)
    data = path.read_bytes()
    return extract_text_from_bytes(data, path.name)


def extract_text_from_raw(text: str) -> str:
    """Pass-through for raw text input; strips leading/trailing whitespace."""
    return text.strip()


# ── Private helpers ────────────────────────────────────────────────────────────

def _from_pdf(data: bytes) -> str:
    # Try pdfplumber first, fall back to PyPDF2
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except ImportError:
        logger.debug("pdfplumber not available, trying PyPDF2")
    except Exception as exc:
        logger.warning("pdfplumber failed: %s — trying PyPDF2", exc)

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except ImportError:
        logger.warning("PyPDF2 not available; returning empty string for PDF")
        return ""
    except Exception as exc:
        logger.warning("PyPDF2 failed: %s", exc)
        return ""


def _from_docx(data: bytes) -> str:
    try:
        import docx  # python-docx
        doc = docx.Document(io.BytesIO(data))
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except ImportError:
        logger.warning("python-docx not available; returning empty string for DOCX")
        return ""
    except Exception as exc:
        logger.warning("python-docx failed: %s", exc)
        return ""


def _from_text_bytes(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace").strip()
