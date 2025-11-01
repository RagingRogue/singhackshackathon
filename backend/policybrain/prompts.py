# policybrain/prompts.py
COMPARE_PROMPT = """You are a careful assistant. Compare the two policies' medical benefits using the normalized JSON.
Answer tersely and include the normalized numbers with units (SGD)."""

EXPLAIN_PROMPT = """Explain what 'medical expenses whilst overseas' covers, using the policy's language.
Cite the Schedule of Benefits and relevant sections where possible."""

SCENARIO_PROMPT = """Given the user scenario and extracted trip details, recommend the most suitable plan,
balancing price and medical coverage. Justify with simple, concrete language."""
