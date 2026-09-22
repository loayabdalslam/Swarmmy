"""
Google Gemini: Security Code Audit Swarm
========================================
Demonstrates using Gemini with specialized security reviewer personas
and extracting the candidate scores and peer critiques.
"""

import json
import os
from swarmmy import Config, create_provider, run_sync


VULNERABLE_CODE = """
def authenticate_user(user_input_token, stored_hash):
    # Timing attack vulnerability: non-constant time comparison
    if user_input_token == stored_hash:
        return True
    return False
"""


def main():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            prompt = messages[0]["content"]
            if "Evaluate each peer solution" in prompt:
                data = json.loads(prompt[prompt.index('{"task"'):])
                return json.dumps([{"id": c["id"], "score": 0.95, "critique": "Correctly identified timing attack."} for c in data["material"]])
            return "Security Recommendation: Use hmac.compare_digest to prevent side-channel timing attacks."
    else:
        backend = create_provider("gemini", model="gemini-2.0-flash")

    # AppSec reviewer personas
    security_roles = [
        "Cryptographer: Focus on constant-time operations, side-channel attacks, and timing leaks.",
        "DevSecOps Lead: Focus on secure coding guidelines, OWASP standards, and unit test verification.",
        "Code Quality Architect: Focus on Python idioms, docstrings, type hinting, and readability."
    ]

    config = Config(agents=3, rounds=1, roles=security_roles, live=True)

    task = f"Audit the following authentication snippet for security vulnerabilities and provide hardened code:\n\n{VULNERABLE_CODE}"

    result = run_sync(task, backend=backend, config=config)

    print("\n" + "=" * 70)
    print("🛡️ AUDIT REPORT & HARDENED CODE:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
