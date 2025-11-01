from groq import Groq
from core.config import GROQ_API_KEY
from services.risk_service import get_destination_info
import json, os

client = Groq(api_key=GROQ_API_KEY)

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

def load_prompt(file_name: str):
    """Load any JSON prompt file from /prompts folder."""
    path = os.path.join(PROMPT_DIR, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load persona and scenario configs
BASE_PROMPT = load_prompt("base_persona.json")
RISK_CONTEXT = load_prompt("context_risk.json")

def build_system_prompt(context: str, scenario: str = "risk_advisory") -> str:
    """Combine persona and scenario JSONs into a single structured system prompt."""
    scenario_cfg = RISK_CONTEXT if scenario == "risk_advisory" else None

    system_prompt = {
        "persona": BASE_PROMPT,
        "scenario": scenario_cfg,
        "backend_context": context,
        "rules": BASE_PROMPT["rules"]
    }
    return json.dumps(system_prompt, indent=2)  # send JSON string to LLM

def ask_llm(user_input: str):
    """Query LLM with structured JSON context and enforce grounding."""
    # Detect destination from user input
    dest_info = None
    for dest_candidate in [
        "Japan", "Thailand", "Vietnam", "USA", "UK", "China",
        "Australia", "Malaysia", "Indonesia", "France", "Germany", "Hong Kong"
    ]:
        if dest_candidate.lower() in user_input.lower():
            dest_info = get_destination_info(dest_candidate)
            break

    if not dest_info:
        return "I don’t have backend data for that destination yet."

    # Build backend JSON context
    context = {
        "destination": dest_info["destination"],
        "risk_score": dest_info["risk_score"],
        "avg_claim_cost": dest_info["avg_claim_cost"],
        "peak_months": dest_info["peak_months"],
        "dominant_claims": dest_info["dominant_claims"],
        "recommended_plan": dest_info["recommendation"]
    }

    # Build strict system prompt (as JSON)
    system_prompt = build_system_prompt(context, scenario="risk_advisory")

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.2,
        max_completion_tokens=800,
    )

    return completion.choices[0].message.content.strip() + "\n\n_(source: backend dataset)_"
