# demos/demo_quote.py
from policybrain.normalize import normalize_policy
from policybrain.quote_builder import build_quote

def pick_med_limit(benefit):
    if benefit.max_limit:
        return benefit.max_limit
    if getattr(benefit, "age_bands", None):
        return max(benefit.age_bands.values())
    return 0.0

def main():
    cases = [
        ("TravelEasy", "data/Policy_Wordings/TravelEasy Policy QTD032212.pdf"),
        ("Scootsurance", "data/Policy_Wordings/Scootsurance QSR022206_updated.pdf"),
    ]
    # Example traveller profile (adjust to taste)
    age = 30
    destination_risk = "standard"     # low | standard | high
    include_cancellation = False
    trip_cost = 0.0                    # set if include_cancellation = True

    for name, path in cases:
        p = normalize_policy(path, name)
        med = p.benefits["medical"]
        med_limit = pick_med_limit(med)

        q = build_quote(
            product_name=name,
            trip_days=10,
            medical_limit=med_limit,
            currency=med.currency or "SGD",
            age=age,
            destination_risk=destination_risk,
            include_cancellation=include_cancellation,
            trip_cost=trip_cost,
            plan_tier="base",          # or "plus"/"elite"
            gst_pct=0.09,              # SG GST 9%
            minimum_premium=25.0,      # sensible floor
        )

        print(
            f"{q['product']:12}  {q['trip_days']:>2}d  "
            f"Medical {q['currency']} {int(q['medical_limit']):,}  "
            f"→ Premium SGD {q['premium_sgd']:.2f}"
        )
        # Optional: show a compact breakdown
        bd = q["breakdown"]
        print(
            f"    breakdown: core={bd['pretax_core']:.2f}, "
            f"age×dest×tier={bd['age_multiplier']:.2f}×{bd['destination_multiplier']:.2f}×{bd['plan_tier_multiplier']:.2f}, "
            f"cancel={bd['cancellation_premium']:.2f}, "
            f"pretax={bd['pretax_total_after_floor']:.2f}, tax={bd['tax_amount']:.2f}"
        )

if __name__ == "__main__":
    main()
