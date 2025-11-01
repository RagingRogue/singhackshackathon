# policybrain/normalize.py
from __future__ import annotations

import re
from typing import Dict, Any, List, Tuple, Optional

from .pdf_io import load_pdf_with_pages
from .rules import extract_medical_from_pdf  # your robust medical parser
from .models import Policy, Eligibility, Benefit, Exclusions, Citation

# -------------------------------------------------------------------
# Fallback / lightweight patterns for eligibility & exclusions
# (Kept here to avoid coupling to rules.py; medical stays in rules.py)
# -------------------------------------------------------------------

# "from 1 to 74 years" / "between 1 and 74 years"
AGE_RANGE_PAT = re.compile(
    r"(?:age|aged)\s*(?:from|between)?\s*(\d{1,2}).{0,20}(\d{1,2})\s*years",
    re.I,
)

# "trip duration up to 183 days", "maximum trip length 183 days"
TRIP_DUR_PAT = re.compile(
    r"(?:trip\s*(?:duration|length).{0,40}?(?:up to|maximum).{0,10}?)(\d{1,3})\s*(?:day|days)",
    re.I,
)

# Residency (very soft)
RESIDENCY_PAT = re.compile(
    r"(?:resident|residency).{0,20}?(?:singapore|sg)\b",
    re.I,
)

# Exclusions – pre-existing, high-risk activities, war/terrorism (soft)
PRE_EXISTING_PAT = re.compile(
    r"pre-?\s*existing.*?(?:excluded|not covered|no\s+cover|exclusion|and its complications)",
    re.I | re.S,
)

HIGH_RISK_PAT = re.compile(
    r"(?:high[-\s]*risk|hazardous).*?(?:activities|sports)|(?:off[-\s]*piste|mountaineering|scuba|ultra[-\s]*marathon)",
    re.I,
)

WAR_TERROR_PAT = re.compile(
    r"(?:war|invasion|enemy|terrorism|terrorist|civil commotion|riot).*?(?:exclusion|not covered|no\s+cover|will not cover)?",
    re.I | re.S,
)


def _find_first(pages: List[Tuple[int, str]], pat: re.Pattern) -> Tuple[Optional[int], Optional[re.Match]]:
    for pno, txt in pages:
        m = pat.search(txt)
        if m:
            return pno, m
    return None, None


def _collect_snippet(text: str, m: re.Match, span_pad: int = 160) -> str:
    a, b = m.span()
    a = max(0, a - span_pad)
    b = min(len(text), b + span_pad)
    snip = text[a:b].strip()
    # collapse whitespace
    snip = re.sub(r"[ \t]+", " ", snip)
    return snip


# -----------------------
# Normalization main API
# -----------------------

def normalize_policy(pdf_path: str, product_name: str) -> Policy:
    """
    Normalize a policy PDF into a consistent Policy object:
      - benefits.medical populated by robust extractor (rules.extract_medical_from_pdf)
      - eligibility (min/max age, residency, trip duration) via light regex
      - exclusions (pre-existing, high-risk, war & terrorism) via light regex
    """
    pages: List[Tuple[int, str]] = load_pdf_with_pages(pdf_path)

    # -------- Benefits: Medical (robust rules.py implementation) --------
    med_raw: Dict[str, Any] = extract_medical_from_pdf(pages, pdf_path)
    medical_benefit = Benefit(
        currency=med_raw.get("currency", "SGD"),
        max_limit=med_raw.get("max_limit"),
        per=med_raw.get("per", "trip"),
        sublimits=med_raw.get("sublimits", {}),
        deductible=med_raw.get("deductible"),
        notes=med_raw.get("notes"),
        citations=[
            Citation(pdf=c["pdf"], page=c.get("page", 1), text_snippet=c.get("text_snippet", ""))
            for c in med_raw.get("citations", [])
        ],
        age_bands=med_raw.get("age_bands", {}),
    )
    benefits: Dict[str, Benefit] = {"medical": medical_benefit}

    # -------- Eligibility (soft, but resilient) --------
    elig_citations: List[Citation] = []
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    trip_duration_max_days: Optional[int] = None
    residency: Optional[str] = None

    p_age, m_age = _find_first(pages, AGE_RANGE_PAT)
    if m_age:
        try:
            min_age = int(m_age.group(1))
            max_age = int(m_age.group(2))
            snip = _collect_snippet(pages[(p_age or 1) - 1][1], m_age) if p_age else m_age.group(0)
            elig_citations.append(Citation(pdf=pdf_path, page=p_age or 1, text_snippet=snip))
        except Exception:
            pass

    p_dur, m_dur = _find_first(pages, TRIP_DUR_PAT)
    if m_dur:
        try:
            trip_duration_max_days = int(m_dur.group(1))
            snip = _collect_snippet(pages[(p_dur or 1) - 1][1], m_dur) if p_dur else m_dur.group(0)
            elig_citations.append(Citation(pdf=pdf_path, page=p_dur or 1, text_snippet=snip))
        except Exception:
            pass

    p_res, m_res = _find_first(pages, RESIDENCY_PAT)
    if m_res:
        residency = "Singapore resident"
        snip = _collect_snippet(pages[(p_res or 1) - 1][1], m_res) if p_res else m_res.group(0)
        elig_citations.append(Citation(pdf=pdf_path, page=p_res or 1, text_snippet=snip))

    eligibility = Eligibility(
        min_age=min_age,
        max_age=max_age,
        residency=residency,
        trip_duration_max_days=trip_duration_max_days,
        citations=elig_citations,
    )

    # -------- Exclusions (soft capture with citations) --------
    excl_citations: List[Citation] = []

    pre_existing_txt: Optional[str] = None
    p_pre, m_pre = _find_first(pages, PRE_EXISTING_PAT)
    if m_pre:
        pre_existing_txt = _collect_snippet(pages[(p_pre or 1) - 1][1], m_pre) if p_pre else m_pre.group(0)
        excl_citations.append(Citation(pdf=pdf_path, page=p_pre or 1, text_snippet=pre_existing_txt))

    high_risk_txt: Optional[str] = None
    p_hr, m_hr = _find_first(pages, HIGH_RISK_PAT)
    if m_hr:
        high_risk_txt = _collect_snippet(pages[(p_hr or 1) - 1][1], m_hr) if p_hr else m_hr.group(0)
        excl_citations.append(Citation(pdf=pdf_path, page=p_hr or 1, text_snippet=high_risk_txt))

    war_terror_txt: Optional[str] = None
    p_wt, m_wt = _find_first(pages, WAR_TERROR_PAT)
    if m_wt:
        war_terror_txt = _collect_snippet(pages[(p_wt or 1) - 1][1], m_wt) if p_wt else m_wt.group(0)
        excl_citations.append(Citation(pdf=pdf_path, page=p_wt or 1, text_snippet=war_terror_txt))

    exclusions = Exclusions(
        pre_existing=pre_existing_txt,
        high_risk_activities=high_risk_txt,
        war_terrorism=war_terror_txt,
        citations=excl_citations,
    )

    # -------- Assemble Policy --------
    policy = Policy(
        product_name=product_name,
        version=None,
        eligibility=eligibility,
        benefits=benefits,
        exclusions=exclusions,
    )
    return policy
