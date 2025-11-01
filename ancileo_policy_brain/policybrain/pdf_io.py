# policybrain/pdf_io.py
from typing import List, Tuple, Dict, Any
import pdfplumber

def load_pdf_with_pages(path: str) -> List[Tuple[int, str]]:
    """
    Return a list of (1-based page_number, extracted_text) tuples.
    """
    pages: List[Tuple[int, str]] = []
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages, start=1):
            pages.append((i, p.extract_text() or ""))
    return pages

def load_pdf_text_and_tables(path: str):
    """
    Return:
      pages:  List[Tuple[int, str]]  -> (1-based page_number, text)
      tables: List[Dict]             -> {"page": int, "table": List[List[str]]}
    """
    pages: List[Tuple[int, str]] = []
    tables: List[Dict[str, Any]] = []
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages, start=1):
            txt = p.extract_text() or ""
            pages.append((i, txt))
            try:
                raw_tables = p.extract_tables() or []
                for t in raw_tables:
                    norm = []
                    for row in (t or []):
                        norm.append([(c or "").strip() for c in row])
                    if norm:
                        tables.append({"page": i, "table": norm})
            except Exception:
                # tables are best-effort; don't crash if one page fails
                pass
    return pages, tables
