# policybrain/quote_builder.py
from __future__ import annotations
from typing import Dict, List, Optional

# ---------------------------
# Tunable pricing parameters
# ---------------------------
# Calibrated so that a typical trip (10d, SGD 100k medical, age 30, standard risk)
# lands ~SGD 50 incl. GST=9%.
BASE_PREMIUM = 8.00               # per policy
RATE_PER_DAY = 1.80               # per day
RATE_PER_1000_MED = 0.20          # per $1,000 of medical limit (flat per trip)

# Optional add-ons (off by default unless passed into build_quote)
CANCEL_RATE_OF_TRIPCOST = 0.035   # 3.5% of declared trip cost if cancellation cover is added

# Loadings / multipliers
AGE_LOADS = [
    (0,   17, 0.90),
    (18,  59, 1.00),
    (60,  69, 1.40),
    (70,  74, 1.90),
    (75, 200, 2.80),
]

DEST_RISK_LOAD = {
    # "region"/risk ⇒ multiplier
    "low":       0.95,
    "standard":  1.00,
    "high":      1.20,
}

PLAN_TIER_LOAD = {
    # Optional cosmetic tiers (applied last, after destination)
    "base":   1.00,
    "plus":   1.10,
    "elite":  1.25,
}

DEFAULT_GST_PCT = 0.09            # Singapore GST 9%
MINIMUM_PREMIUM = 25.00           # floor (before tax), helps avoid ultra-cheap quotes
ROUND_TO = 0.05                   # round to nearest 5 cents


def _round_to_step(value: float, step: float) -> float:
    if step <= 0:
        return round(value, 2)
    units = round(value / step)
    return round(units * step + 1e-9, 2)


def _age_multiplier(age: Optional[int]) -> float:
    if age is None:
        return 1.0
    for lo, hi, mult in AGE_LOADS:
        if lo <= age <= hi:
            return mult
    return AGE_LOADS[-1][2]


def _dest_multiplier(risk: str) -> float:
    return DEST_RISK_LOAD.get((risk or "standard").lower(), 1.0)


def _tier_multiplier(tier: str) -> float:
    return PLAN_TIER_LOAD.get((tier or "base").lower(), 1.0)


def _compute_pretax(
    trip_days: int,
    medical_limit: float,
) -> float:
    days = max(int(trip_days or 0), 0)
    med = max(float(medical_limit or 0.0), 0.0)
    # Core pricing components
    base = BASE_PREMIUM
    day_component = RATE_PER_DAY * days
    med_component = RATE_PER_1000_MED * (med / 1000.0)
    return base + day_component + med_component


def build_quote(
    *,
    product_name: str,
    trip_days: int,
    medical_limit: float,
    currency: str = "SGD",
    # Optional realism knobs:
    age: Optional[int] = None,
    destination_risk: str = "standard",          # one of DEST_RISK_LOAD keys
    plan_tier: str = "base",                     # "base" | "plus" | "elite"
    include_cancellation: bool = False,
    trip_cost: float = 0.0,                      # used if include_cancellation=True
    gst_pct: float = DEFAULT_GST_PCT,            # 0.09 for SG
    minimum_premium: float = MINIMUM_PREMIUM,    # floor before GST
) -> Dict:
    """
    Returns a quote dict with a realistic premium and a transparent breakdown.
    """
    pretax_core = _compute_pretax(trip_days, medical_limit)

    # Loadings
    age_mult = _age_multiplier(age)
    dest_mult = _dest_multiplier(destination_risk)
    tier_mult = _tier_multiplier(plan_tier)

    loaded = pretax_core * age_mult * dest_mult * tier_mult

    # Optional cancellation
    cancel_premium = 0.0
    if include_cancellation and trip_cost and trip_cost > 0:
        cancel_premium = max(trip_cost * CANCEL_RATE_OF_TRIPCOST, 0.0)

    pretax_total = loaded + cancel_premium

    # Minimum premium floor (pre-tax)
    pretax_total = max(pretax_total, minimum_premium)

    # Taxes/fees
    tax_amount = pretax_total * max(gst_pct, 0.0)
    total = pretax_total + tax_amount

    # Friendly rounding
    pretax_total = _round_to_step(pretax_total, ROUND_TO)
    tax_amount   = _round_to_step(tax_amount, ROUND_TO)
    total        = _round_to_step(total, ROUND_TO)

    return {
        "product": product_name,
        "currency": currency,
        "trip_days": int(trip_days),
        "medical_limit": float(medical_limit or 0.0),
        "include_cancellation": bool(include_cancellation),
        "trip_cost": float(trip_cost or 0.0),
        "age": age,
        "destination_risk": destination_risk,
        "plan_tier": plan_tier,
        "gst_pct": gst_pct,
        "minimum_premium_floor": minimum_premium,
        "premium_sgd": total,
        "breakdown": {
            "base_premium": BASE_PREMIUM,
            "rate_per_day": RATE_PER_DAY,
            "rate_per_1000_med": RATE_PER_1000_MED,
            "age_multiplier": age_mult,
            "destination_multiplier": dest_mult,
            "plan_tier_multiplier": tier_mult,
            "pretax_core": round(pretax_core, 2),
            "cancellation_premium": round(cancel_premium, 2),
            "pretax_total_after_floor": pretax_total,
            "tax_amount": tax_amount,
        },
    }


def build_quotes(
    items: List[Dict],
    *,
    gst_pct: float = DEFAULT_GST_PCT,
    minimum_premium: float = MINIMUM_PREMIUM,
) -> List[Dict]:
    """
    Convenience for batch quoting.
    Each item must have: product_name, trip_days, medical_limit, currency (optional),
    and may include: age, destination_risk, plan_tier, include_cancellation, trip_cost.
    """
    results = []
    for it in items:
        q = build_quote(
            product_name=it["product_name"],
            trip_days=it["trip_days"],
            medical_limit=it["medical_limit"],
            currency=it.get("currency", "SGD"),
            age=it.get("age"),
            destination_risk=it.get("destination_risk", "standard"),
            plan_tier=it.get("plan_tier", "base"),
            include_cancellation=it.get("include_cancellation", False),
            trip_cost=it.get("trip_cost", 0.0),
            gst_pct=gst_pct,
            minimum_premium=minimum_premium,
        )
        results.append(q)
    return results
