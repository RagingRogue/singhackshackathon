# policybrain/models.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class Citation:
    pdf: str
    page: int
    text_snippet: str

@dataclass
class Benefit:
    currency: str = "SGD"
    max_limit: Optional[float] = None
    per: Optional[str] = None        # "trip" | "day" | "person" | "family"
    sublimits: Dict[str, float] = field(default_factory=dict)
    deductible: Optional[float] = None
    notes: Optional[str] = None
    citations: List[Citation] = field(default_factory=list)
    # Optional — used to choose limits by traveler age
    age_bands: Dict[str, float] = field(default_factory=dict)

@dataclass
class Eligibility:
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    residency: Optional[str] = None
    trip_duration_max_days: Optional[int] = None
    citations: List[Citation] = field(default_factory=list)

@dataclass
class Exclusions:
    pre_existing: Optional[str] = None
    high_risk_activities: Optional[str] = None
    war_terrorism: Optional[str] = None
    citations: List[Citation] = field(default_factory=list)

@dataclass
class Policy:
    product_name: str
    version: Optional[str]
    eligibility: Eligibility
    benefits: Dict[str, Benefit]
    exclusions: Exclusions

    def to_json(self) -> Dict[str, Any]:
        def _ser(x):
            if isinstance(x, list):
                return [_ser(i) for i in x]
            if hasattr(x, "__dataclass_fields__"):
                d = asdict(x)
                return d
            if isinstance(x, dict):
                return {k: _ser(v) for k, v in x.items()}
            return x
        return _ser(self)
