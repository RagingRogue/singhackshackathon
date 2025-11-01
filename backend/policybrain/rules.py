import re
from typing import Any, Dict, List, Tuple

NUM = r"(?:\d{1,3}(?:[,\u00A0\u2009\u202F' ]\d{3})+|\d+)(?:\.\d+)?"
CURRENCY = r"(?:SGD|S\$|\$)"

def _norm_spaces(s: str) -> str:
    s = s.replace("\u00A0", " ").replace("\u2009", " ").replace("\u202F", " ")
    s = s.replace("-\n", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s

def _safe_num(nstr: str | None, unit_tail: str | None = None) -> float | None:
    if not nstr:
        return None
    try:
        v = float(nstr.replace(",", "").replace(" ", "").replace("'", ""))
    except Exception:
        return None
    tail = (unit_tail or "").lower()
    if re.search(r"\b(million|m)\b", tail):
        v *= 1_000_000.0
    elif re.search(r"\b(k|thousand)\b", tail):
        v *= 1_000.0
    return v

def _choose_amount(m: re.Match) -> float | None:
    n = m.group(1) if m.lastindex and m.lastindex >= 1 else None
    u = m.group(2) if m.lastindex and m.lastindex >= 2 else None
    return _safe_num(n, u)

def _add_cite(out: Dict[str, Any], pdf_path: str, page: int, snippet: str) -> None:
    out["citations"].append({
        "pdf": pdf_path,
        "page": page,
        "text_snippet": _norm_spaces(snippet)[:400]
    })

def _looks_traveleasy(path: str) -> bool:
    p = path.lower()
    return "traveleasy" in p or "qtd" in p

def _looks_scootsurance(path: str) -> bool:
    p = path.lower()
    return "scootsurance" in p or "qsr" in p or "scoot" in p

def extract_medical_from_pdf(
    pages: List[Tuple[int, str]],
    pdf_path: str
) -> Dict[str, Any]:
    """
    Returns:
      {
        "currency": "SGD",
        "max_limit": float|None,
        "per": "trip"|"day",
        "sublimits": {"tcm": float, "dental": float, ...},
        "deductible": None|float,
        "notes": str|None,
        "citations": [],
        "age_bands": {"12-69": float, "70-74": float, "<12": float}
      }
    """
    norm_pages: List[Tuple[int, str]] = [(pno, _norm_spaces(txt)) for (pno, txt) in pages]
    full = "\n".join(t for _, t in norm_pages)

    out: Dict[str, Any] = {
        "currency": "SGD",
        "max_limit": None,
        "per": "trip",
        "sublimits": {},
        "deductible": None,
        "notes": None,
        "citations": [],
        "age_bands": {},
    }

    is_te = _looks_traveleasy(pdf_path)
    is_sc = _looks_scootsurance(pdf_path)

    # -----------------------------
    # TravelEasy: lock onto the exact row wording
    # -----------------------------
    if is_te:
        # Very specific key used in TravelEasy SoB tables
        TE_MED_RX = re.compile(
            rf"(?:Medical\s+expenses\s+whilst\s+overseas).*?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
            re.I | re.S
        )
        for pno, text in norm_pages:
            m = TE_MED_RX.search(text)
            if m:
                amt = _choose_amount(m)
                if amt is not None:
                    out["max_limit"] = amt
                    out["per"] = "trip"  # TravelEasy is per trip for this line
                    _add_cite(out, pdf_path, pno, m.group(0))
                    break

    # -----------------------------
    # Scootsurance: pick adult band
    # -----------------------------
    if is_sc and out["max_limit"] is None:
        ADULT_RX = re.compile(
            rf"(?:12\s*to\s*69\s*years\s*old|adult).*?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
            re.I | re.S
        )
        for pno, text in norm_pages:
            m = ADULT_RX.search(text)
            if m:
                amt = _choose_amount(m)
                if amt is not None:
                    out["max_limit"] = amt
                    # Per day noise appears frequently on other lines; keep 'trip' unless "per day" is within 120 chars of this match
                    window = text[max(0, m.start()-60): m.end()+60].lower()
                    if re.search(r"\bper\s+day\b", window):
                        out["per"] = "day"
                    else:
                        out["per"] = "trip"
                    _add_cite(out, pdf_path, pno, m.group(0))
                    break

    # -----------------------------
    # Fallback (any product) if still missing: a generic medical row
    # -----------------------------
    if out["max_limit"] is None:
        GEN_MED_RX = re.compile(
            rf"(?:Medical\s+(?:Expenses|benefits).*?|Medical\s+expenses\s+whilst\s+overseas).*?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
            re.I | re.S
        )
        for pno, text in norm_pages:
            m = GEN_MED_RX.search(text)
            if m:
                amt = _choose_amount(m)
                if amt is not None:
                    out["max_limit"] = amt
                    _add_cite(out, pdf_path, pno, m.group(0))
                    # Set 'per' only if the token is close to the capture to avoid global false "per day"
                    window = text[max(0, m.start()-80): m.end()+80].lower()
                    if re.search(r"\bper\s+day\b", window):
                        out["per"] = "day"
                    elif re.search(r"\bper\s+trip\b", window):
                        out["per"] = "trip"
                break

    # -----------------------------
    # Age bands (guarded)
    # -----------------------------
    bands = [
        (r"(?:12\s*to\s*69\s*years\s*old|adult)", "12-69"),
        (r"70\s*to\s*74\s*years\s*old", "70-74"),
        (r"(?:below|under)\s*12\s*years\s*old", "<12"),
    ]
    for pat, key in bands:
        rx = re.compile(
            rf"{pat}.*?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
            re.I | re.S
        )
        for pno, text in norm_pages:
            mm = rx.search(text)
            if mm:
                amt = _choose_amount(mm)
                if amt is not None:
                    out["age_bands"][key] = amt
                    _add_cite(out, pdf_path, pno, mm.group(0))
                break

    # -----------------------------
    # TCM sub-limit: capture only if TCM is in same row/nearby
    #   - Scootsurance has "Pays up to $750 for TCM Treatment" near Medical
    #   - TravelEasy lists "Traditional Chinese medicine expenses" as its own line; only capture if a clear amount follows
    # -----------------------------
    TCM_NEAR_RX = re.compile(
        rf"(?:TCM|Traditional\s+Chinese\s+medicine)[^.\n\r]{{0,80}}?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
        re.I | re.S
    )
    for pno, text in norm_pages:
        m = TCM_NEAR_RX.search(text)
        if m:
            amt = _choose_amount(m)
            if amt is not None and amt > 0:
                out["sublimits"]["tcm"] = amt
                _add_cite(out, pdf_path, pno, m.group(0))
            break

    # Dental (emergency dental)
    DENTAL_RX = re.compile(
        rf"(?:Emergency\s+Dental\s+Expenses|Dental\s+Expenses)[^.\n\r]{{0,80}}?(?:{CURRENCY})\s*({NUM})(?:\s*(million|m|k|thousand))?",
        re.I | re.S
    )
    for pno, text in norm_pages:
        m = DENTAL_RX.search(text)
        if m:
            amt = _choose_amount(m)
            if amt is not None and amt > 0:
                out["sublimits"]["dental"] = amt
                _add_cite(out, pdf_path, pno, m.group(0))
            break

    # Currency normalization
    if re.search(r"\bSGD\b|S\$", full):
        out["currency"] = "SGD"
    else:
        out["currency"] = "SGD"  # default for SG policies

    # Sanity filters
    if out["max_limit"] is not None and out["max_limit"] < 10_000:
        out["notes"] = ((out["notes"] + " | ") if out["notes"] else "") + \
            "Low medical limit detected; verify against Schedule of Benefits."

    # If a sublimit accidentally exceeds the main limit (common OCR glitch), drop it.
    if out["max_limit"] is not None:
        for k in list(out["sublimits"].keys()):
            if out["sublimits"][k] and out["sublimits"][k] > 1.2 * out["max_limit"]:
                del out["sublimits"][k]

    return out
