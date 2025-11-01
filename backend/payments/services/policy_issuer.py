import json
from pathlib import Path
from datetime import datetime

# Save issued policy to data/issued_policies.json
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
POLICY_FILE = DATA_DIR / "issued_policies.json"

def generate_policy(email: str, session_id: str):
    policy = {
        "policy_id": f"POL-{session_id}",
        "email": email,
        "issued_at": datetime.now().isoformat(),
        "status": "Active",
        "message": "✅ Policy successfully issued!"
    }

    if POLICY_FILE.exists():
        with open(POLICY_FILE, "r") as file:
            policies = json.load(file)
    else:
        policies = []

    policies.append(policy)
    with open(POLICY_FILE, "w") as file:
        json.dump(policies, file, indent=4)

    return policy
