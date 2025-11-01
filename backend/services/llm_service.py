import json
import os
from groq import Groq
from core.config import GROQ_API_KEY
from policybrain.normalize import normalize_policy
from policybrain.quote_builder import build_quote

# --- 1️⃣ Connect to Groq ---
client = Groq(api_key=GROQ_API_KEY)

# --- 2️⃣ Load insurance knowledge base ---
with open("data/insurance_risk_knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)


# --- 3️⃣ Helper: find matching destination ---
def find_destination_info(dest: str):
    """Find destination info from the JSON knowledge base."""
    for record in KNOWLEDGE:
        if record["destination"].lower() == dest.lower():
            return record
    return None


# --- 4️⃣ Helper: select medical limit for quoting ---
def pick_med_limit(benefit):
    if getattr(benefit, "max_limit", None):
        return benefit.max_limit
    if getattr(benefit, "age_bands", None):
        return max(benefit.age_bands.values())
    return 0.0


# --- 5️⃣ Helper: build a quote dynamically ---
def get_quote(product_path, product_name, age, destination_risk, trip_days=10):
    try:
        policy = normalize_policy(product_path, product_name)
        med = policy.benefits["medical"]
        med_limit = pick_med_limit(med)

        quote = build_quote(
            product_name=product_name,
            trip_days=trip_days,
            medical_limit=med_limit,
            currency=med.currency or "SGD",
            age=age,
            destination_risk=destination_risk,
            include_cancellation=False,
            trip_cost=0.0,
            gst_pct=0.09,
            minimum_premium=25.0,
        )
        return quote
    except Exception as e:
        print("⚠️ Quote generation failed:", e)
        return None


# --- 6️⃣ Main LLM reasoning function ---
def ask_llm(user_input):
    """
    Takes a user's message, extracts destination, computes risk,
    builds quotes for available policies, and sends context + reasoning to Groq LLM.
    """

    # Defensive input handling
    if not isinstance(user_input, str):
        try:
            if isinstance(user_input, list) and len(user_input) > 0:
                user_input = user_input[0]
            elif isinstance(user_input, dict):
                user_input = user_input.get("message", user_input.get("text", str(user_input)))
            else:
                user_input = str(user_input)
        except Exception:
            user_input = str(user_input)

    # Destination matching
    dest = None
    info = None
    for record in KNOWLEDGE:
        if record["destination"].lower() in user_input.lower():
            dest = record["destination"]
            info = record
            break

    context = ""
    quotes = []
    adjusted_risk = None

    if info:
        adjusted_risk = info["risk_score"]
        context = (
            f"Destination: {info['destination']}\n"
            f"Risk Score: {info['risk_score']}\n"
            f"Average Claim Cost: {info['avg_claim_cost']} SGD\n"
            f"Peak Months: {', '.join(info['peak_months'])}\n"
            f"Dominant Claim Types: "
            + ", ".join([f"{c['type']} ({c['percentage']}%)" for c in info['dominant_claims']])
            + f"\nInsights based on historical claims data."
        )

        # Quote generation for both policies
        try:
            policy_files = {
                "TravelEasy": "policy_data/Policy_Wordings/TravelEasy Policy QTD032212.pdf",
                "Scootsurance": "policy_data/Policy_Wordings/Scootsurance QSR022206_updated.pdf",
            }

            # Convert risk_score to category
            if adjusted_risk < 0.3:
                risk_label = "low"
            elif adjusted_risk < 0.6:
                risk_label = "standard"
            else:
                risk_label = "high"

            for product_name, product_path in policy_files.items():
                quote = get_quote(
                    product_path=product_path,
                    product_name=product_name,
                    age=30,
                    destination_risk=risk_label,
                    trip_days=10,
                )
                if quote:
                    quotes.append(quote)

        except Exception as e:
            print("⚠️ Quote generation failed:", e)

    # --- Build AI prompt ---
    system_prompt = (
        "You are an AI travel insurance advisor. "
        "Use real claim data and policy information to compare plans "
        "and recommend the best option for the user's trip. "
        "Always explain your reasoning clearly and concisely."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Add context
    if context:
        messages.append({"role": "assistant", "content": f"Context:\n{context}"})

    # Add quote details
    if quotes:
        quote_text = "\n\n".join(
            [
                f"Quote for {q['product']}: {q['currency']} {int(q['medical_limit']):,} medical coverage, "
                f"{q['trip_days']} days, estimated premium SGD {q['premium_sgd']:.2f} "
                f"(core={q['breakdown']['pretax_core']:.2f}, tax={q['breakdown']['tax_amount']:.2f})"
                for q in quotes
            ]
        )
        messages.append({"role": "assistant", "content": f"Available Quotes:\n{quote_text}"})

    messages.append({"role": "user", "content": user_input})

    # Call Groq
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.8,
        max_completion_tokens=1024,
    )

    return completion.choices[0].message.content.strip()