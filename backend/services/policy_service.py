import json
import os

def load_mock_policies():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_policies.json")
    with open(data_path, "r") as f:
        return json.load(f)

def compare_policies(plan_a, plan_b):
    policies = load_mock_policies()

    # normalize keys (case-insensitive matching)
    plan_a_key = next((k for k in policies if k.lower() == plan_a.lower()), None)
    plan_b_key = next((k for k in policies if k.lower() == plan_b.lower()), None)

    if not plan_a_key or not plan_b_key:
        available = ", ".join(policies.keys())
        return f"Sorry, I can only compare {available} for now."

    a = policies[plan_a_key]
    b = policies[plan_b_key]

    print(f"DEBUG → Comparing {plan_a_key} vs {plan_b_key}")

    comparison = [f"### 📊 Comparing **{plan_a_key}** vs **{plan_b_key}**\n"]

    for key in a:
        if a[key] == b[key]:
            comparison.append(f"✅ Both cover **{key.replace('_',' ')}** equally: {a[key]}")
        else:
            comparison.append(f"🔹 **{plan_a_key}**: {a[key]} vs **{plan_b_key}**: {b[key]}")

    return "\n".join(comparison)

def explain_policy(plan_name):
    policies = load_mock_policies()
    plan_key = next((k for k in policies if k.lower() == plan_name.lower()), None)

    if not plan_key:
        return f"Sorry, I only have data for {', '.join(policies.keys())}."

    plan = policies[plan_key]
    explanation = [f"### 🧾 Coverage summary for **{plan_key}**\n"]

    for key, value in plan.items():
        key_fmt = key.replace("_", " ").capitalize()
        explanation.append(f"- **{key_fmt}**: {value}")

    return "\n".join(explanation)
