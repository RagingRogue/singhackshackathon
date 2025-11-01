# policybrain/trip_extract.py
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dateutil import parser as dtp
from .pdf_io import load_pdf_with_pages

NUM = r"(?:\d{1,3}(?:[,\u00A0\u2009\u202F' ]\d{3})+|\d+)(?:\.\d+)?"

PNR_PRIMARY = re.compile(
    r"(?:Booking\s*(?:Reference|Code|PNR)\s*(?:\(|\[)?\s*PNR\s*(?:\)|\])?\s*[:\-]?\s*)([A-Z0-9]{5,8})",
    re.I,
)
PNR_ALT_1 = re.compile(
    r"(?:\bPNR\b|\bBooking\s*Reference\b|\bRecord\s*Locator\b)\s*[:\-]?\s*([A-Z0-9]{5,8})",
    re.I,
)
PNR_NEAR = re.compile(r"\b([A-Z0-9]{5,8})\b")

NAME_PATTERN = re.compile(
    r"(?:Passenger\s*(?:Name)?\s*[:\-]?\s*)([A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,3})",
    re.I | re.S,
)

ROUTE_PATTERN = re.compile(r"\b([A-Z]{3})\s*(?:[-–—>→]|(?:\s+to\s+))\s*([A-Z]{3})\b")
DATE_PATTERN = re.compile(
    r"(\b\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}\b|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b)"
)
PRICE_PATTERN = re.compile(rf"(?:Total|Grand\s*Total|Amount).*?(?:S\$|SGD|\$)\s*({NUM})", re.I | re.S)

def _normalize_spaces(s: str) -> str:
    s = s.replace("\u00A0", " ").replace("\u2009", " ").replace("\u202F", " ")
    s = s.replace("-\n", "")
    return re.sub(r"[ \t]+", " ", s)

def _first_match(text: str, pat: re.Pattern) -> str:
    m = pat.search(text)
    return m.group(1).strip() if m else ""

def _parse_all_dates(text: str) -> List[datetime]:
    dates: List[datetime] = []
    for m in DATE_PATTERN.finditer(text):
        raw = m.group(1)
        for dayfirst in (False, True):
            try:
                dates.append(dtp.parse(raw, dayfirst=dayfirst))
                break
            except Exception:
                continue
    # dedupe by date
    seen = set()
    out: List[datetime] = []
    for d in dates:
        k = d.date().isoformat()
        if k not in seen:
            out.append(d)
            seen.add(k)
    return out

def _coerce_money(s: str) -> float:
    try:
        return float(s.replace(",", "").replace(" ", ""))
    except Exception:
        return 0.0

def _find_pnr_with_proximity(text: str) -> str:
    for kw in (r"\bPNR\b", r"\bBooking\s*Reference\b", r"\bRecord\s*Locator\b"):
        for m in re.finditer(kw, text, flags=re.I):
            window = text[m.end(): m.end() + 80]
            m2 = PNR_NEAR.search(window)
            if m2:
                return m2.group(1).strip()
    return ""

def extract_trip_from_pdf(pdf_path: str) -> Dict[str, Any]:
    pages: List[Tuple[int, str]] = load_pdf_with_pages(pdf_path)
    full_text = _normalize_spaces("\n".join(t for _, t in pages))
    out: Dict[str, Any] = {"source_pdf": pdf_path, "citations": []}

    # PNR
    pnr = _first_match(full_text, PNR_PRIMARY) or _first_match(full_text, PNR_ALT_1) or _find_pnr_with_proximity(full_text)
    if pnr:
        out["pnr"] = pnr
        out["citations"].append({"page": 1, "field": "pnr"})

    # Passenger name (trim if email is next token)
    name = _first_match(full_text, NAME_PATTERN)
    if name:
        # strip if immediate "Email" follows
        name = re.sub(r"\s*Email.*$", "", name, flags=re.I)
        out["primary_traveler"] = name.strip()
        out["citations"].append({"page": 1, "field": "primary_traveler"})

    # Route
    r = ROUTE_PATTERN.search(full_text)
    if r:
        out["origin"], out["destination"] = r.group(1), r.group(2)
        out["citations"].append({"page": 1, "field": "route"})

    # Dates
    dates = sorted(_parse_all_dates(full_text))
    if dates:
        out["depart_date"] = dates[0].date().isoformat()
        if len(dates) > 1:
            out["return_date"] = dates[-1].date().isoformat()

    # Price
    m = PRICE_PATTERN.search(full_text)
    if m:
        out["trip_cost_sgd"] = _coerce_money(m.group(1))
        out["citations"].append({"page": 1, "field": "price"})

    return out
