from policybrain.normalize import normalize_policy
from policybrain.quote_builder import build_quote

def pick_med_limit(benefit):
    if benefit.max_limit:
        return benefit.max_limit
    if getattr(benefit, "age_bands", None):
        return max(benefit.age_bands.values())
    return 0.0

def get_quote(product_path, product_name, age, destination_risk, trip_days=10, include_cancellation=False):
    p = normalize_policy(product_path, product_name)
    med = p.benefits["medical"]
    med_limit = pick_med_limit(med)

    q = build_quote(
        product_name=product_name,
        trip_days=trip_days,
        medical_limit=med_limit,
        currency=med.currency or "SGD",
        age=age,
        destination_risk=destination_risk,
        include_cancellation=include_cancellation,
        trip_cost=0.0,
        plan_tier="base",
        gst_pct=0.09,
        minimum_premium=25.0,
    )

    return {
        "product": q["product"],
        "premium": q["premium_sgd"],
        "currency": q["currency"],
        "medical_limit": q["medical_limit"],
        "trip_days": q["trip_days"],
        "breakdown": q["breakdown"]
    }