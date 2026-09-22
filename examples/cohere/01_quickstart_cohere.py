"""
Cohere: Quickstart Swarm Execution
==================================
Demonstrates running a swarm with Cohere Command R+.

Setup:
  1. In PowerShell: $env:COHERE_API_KEY="..."
  2. Run: python examples/cohere/01_quickstart_cohere.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("COHERE_API_KEY")

    if not api_key:
        print("[WARN] COHERE_API_KEY not found in environment.")
        print("       Set it via: $env:COHERE_API_KEY=\"...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Cohere Command R+ completed enterprise task."
    else:
        backend = create_provider("cohere", model="command-r-plus-08-2024")

    config = Config(agents=3, rounds=1, concurrency=3)

    task = "Synthesize an enterprise AI governance framework complying with the EU AI Act."

    print(">>> Starting Swarmmy with Cohere...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
