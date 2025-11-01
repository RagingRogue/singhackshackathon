from groq import Groq
from core.config import GROQ_API_KEY
import json

# Initialize Groq client once
client = Groq(api_key=GROQ_API_KEY)

def parse_message_llm(user_message: str):
    """
    Uses the LLM to classify user intent and extract structured trip details.
    Returns a dictionary like:
    {
        "intent": str,
        "plan_a": str | None,
        "plan_b": str | None,
        "destination": str | None,
        "activities": [str],
        "trip_duration_days": int | None,
        "age": int | None,
        "gender": str | None,
        "medical_conditions": [str]
    }
    """
    prompt = f"""
    You are an information extraction assistant for a travel insurance chatbot.

    Task:
    - Read the user's message.
    - Output **ONLY JSON**, following this schema:
        {{
            "intent": "comparison" | "explanation" | "scenario" | "general",
            "plan_a": string or null,
            "plan_b": string or null,
            "destination": string or null,
            "activities": list of strings,
            "trip_duration_days": integer or null,
            "age": integer or null,
            "gender": string or null,
            "medical_conditions": list of strings
        }}

    Extraction rules:
    - intent: classify based on meaning (compare, explain, scenario, general)
    - plan_a / plan_b: detect plan names (e.g., TravelEasy, Scootsurance)
    - destination: detect country or region of travel
    - activities: detect planned activities (skiing, hiking, diving, shopping, etc.)
    - trip_duration_days: if the user mentions "5 days", "2 weeks", etc., convert to days
    - age, gender, medical_conditions: extract if clearly mentioned, otherwise null/[]
    - If something is not mentioned, leave it null or empty array.
    - Never include any commentary or Markdown—output raw JSON only.

    Examples:

    Input: Compare TravelEasy and Scootsurance for my 2-week ski trip to Japan
    Output: {{
      "intent": "comparison",
      "plan_a": "TravelEasy",
      "plan_b": "Scootsurance",
      "destination": "Japan",
      "activities": ["skiing"],
      "trip_duration_days": 14,
      "age": null,
      "gender": null,
      "medical_conditions": []
    }}

    Input: I’m going hiking in Switzerland for 10 days, which plan do you recommend?
    Output: {{
      "intent": "comparison",
      "plan_a": null,
      "plan_b": null,
      "destination": "Switzerland",
      "activities": ["hiking"],
      "trip_duration_days": 10,
      "age": null,
      "gender": null,
      "medical_conditions": []
    }}

    Input: Tell me about the TravelEasy plan
    Output: {{
      "intent": "explanation",
      "plan_a": "TravelEasy",
      "plan_b": null,
      "destination": null,
      "activities": [],
      "trip_duration_days": null,
      "age": null,
      "gender": null,
      "medical_conditions": []
    }}

    Input: I’m 40 years old and diabetic, going to Bali for snorkeling
    Output: {{
      "intent": "scenario",
      "plan_a": null,
      "plan_b": null,
      "destination": "Bali",
      "activities": ["snorkeling"],
      "trip_duration_days": null,
      "age": 40,
      "gender": null,
      "medical_conditions": ["diabetes"]
    }}

    Now analyze this message and respond with JSON only:
    {user_message}
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_completion_tokens=300,
    )

    raw = completion.choices[0].message.content.strip()
    print("DEBUG → LLM raw output:", raw)

    try:
        result = json.loads(raw)
    except Exception:
        # Safety fallback in case of parsing errors
        result = {
            "intent": "general",
            "plan_a": None,
            "plan_b": None,
            "destination": None,
            "activities": [],
            "trip_duration_days": None,
            "age": None,
            "gender": None,
            "medical_conditions": []
        }

    return result
