from services.llm_service import ask_llm
from services.intent_service import parse_message_llm
from agents.tool_registry import run_tool

def handle_message(user_message: str):
    """
    Handles message routing — decides whether to:
    - run a policy comparison/explanation (using backend tools)
    - or delegate to the LLM for risk-based reasoning (grounded)
    """
    parsed = parse_message_llm(user_message)
    intent = parsed.get("intent")
    plan_a = parsed.get("plan_a")
    plan_b = parsed.get("plan_b")
    destination = parsed.get("destination")

    print(f"DEBUG → Parsed message: {parsed}")

    # --- tool usage ---
    if intent == "comparison" and plan_a and plan_b:
        return run_tool("compare", plan_a, plan_b)

    elif intent == "explanation" and plan_a:
        return run_tool("explanation", plan_a)

    # --- grounded risk reasoning mode ---
    if destination:
        return ask_llm(user_message)  # always pass the raw string

    elif intent == "scenario":
        return "Interesting scenario! I’ll use your details soon to check claim likelihoods."

    return "Could you tell me more about your destination or which plan you're considering?"
