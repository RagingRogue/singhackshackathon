import json
from groq import Groq
from core.config import GROQ_API_KEY

# --- 1️⃣ Connect to Groq ---
client = Groq(api_key=GROQ_API_KEY)

# --- 2️⃣ Load insurance knowledge base ---
with open("data/insurance_risk_knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# --- 3️⃣ Helper: find matching destination ---
def find_destination_info(dest: str):
    """Finds destination info from the JSON knowledge base."""
    for record in KNOWLEDGE:
        if record["destination"].lower() == dest.lower():
            return record
    return None


# --- 4️⃣ Main LLM reasoning function ---
def ask_llm(user_input):
    """
    Takes a user's question or message (string, dict, or list),
    finds relevant destination data,
    and sends both user query + context to Groq's LLM.
    """

    # --- Defensive input handling ---
    if not isinstance(user_input, str):
        try:
            # if it's a list, take the first item
            if isinstance(user_input, list) and len(user_input) > 0:
                user_input = user_input[0]
            # if it's a dict, extract the 'message' key if available
            elif isinstance(user_input, dict):
                if "message" in user_input:
                    user_input = user_input["message"]
                elif "text" in user_input:
                    user_input = user_input["text"]
                else:
                    user_input = str(user_input)
            else:
                user_input = str(user_input)
        except Exception:
            user_input = str(user_input)

    # --- Destination matching ---
    dest = None
    for record in KNOWLEDGE:
        if record["destination"].lower() in user_input.lower():
            dest = record["destination"]
            break

    # --- Build context if destination found ---
    context = ""
    if dest:
        info = find_destination_info(dest)
        if info:
            context = (
                f"Destination: {info['destination']}\n"
                f"Risk Score: {info['risk_score']}\n"
                f"Average Claim Cost: {info['avg_claim_cost']} SGD\n"
                f"Peak Months: {', '.join(info['peak_months'])}\n"
                f"Dominant Claim Types: "
                + ", ".join(
                    [f"{c['type']} ({c['percentage']}%)" for c in info['dominant_claims']]
                )
                + f"\nRecommended Plan: {info['recommendation']}."
            )

    # --- Prompt construction ---
    system_prompt = (
        "You are an AI travel insurance advisor using historical claim data to guide users. "
        "If the user mentions a destination, use the contextual data provided to explain risks "
        "and recommend the most suitable plan (Bronze/Silver/Gold). "
        "Always explain your reasoning briefly and clearly."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    if context:
        messages.insert(1, {"role": "assistant", "content": f"Context:\n{context}"})

    # --- Call Groq model ---
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.8,
        max_completion_tokens=1024,
    )

    return completion.choices[0].message.content.strip()

#For testing

# if __name__ == "__main__":
#     print("🧠 Insurance reasoning test mode activated!\n")
#     print("Type a message like 'I'm traveling to Japan in December' or 'What insurance should I get for Thailand?'")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Goodbye 👋")
#             break
#         try:
#             response = ask_llm(user_input)
#             print("\nAssistant:", response, "\n")
#         except Exception as e:
#             print("⚠️ Error during reasoning:", e, "\n")