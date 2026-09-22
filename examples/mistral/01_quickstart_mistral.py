"""
Mistral AI: Quickstart Swarm Execution
======================================
Demonstrates running a swarm with Mistral Large.

Setup:
  1. In PowerShell: $env:MISTRAL_API_KEY="..."
  2. Run: python examples/mistral/01_quickstart_mistral.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("MISTRAL_API_KEY")

    if not api_key:
        print("[WARN] MISTRAL_API_KEY not found in environment.")
        print("       Set it via: $env:MISTRAL_API_KEY=\"...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Mistral Large swarm completed task."
    else:
        backend = create_provider("mistral", model="mistral-large-latest")

    config = Config(agents=3, rounds=1, concurrency=3)

    task = "Propose a disaster recovery runbook for an enterprise PostgreSQL cluster using Patroni."

    print(">>> Starting Swarmmy with Mistral AI...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
