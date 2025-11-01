from services.policy_service import compare_policies, explain_policy

TOOLS = {
    "compare": compare_policies,
    "explanation": explain_policy
}

def run_tool(intent, *args):
    """
    Looks up a backend function by name and runs it.
    Returns the result or None if no tool exists.
    """
    func = TOOLS.get(intent)
    return func(*args) if func else None

