"""
OpenAI: Quickstart Swarm Deliberation
====================================
Demonstrates standard bounded peer-review swarm execution with OpenAI (gpt-4o-mini).

Setup:
  1. In PowerShell: $env:OPENAI_API_KEY="sk-..."
  2. Run: python examples/openai/01_quickstart_openai.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[WARN] OPENAI_API_KEY not found in environment.")
        print("       Set it via: $env:OPENAI_API_KEY=\"sk-...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: OpenAI swarm completed task with bounded budget."
    else:
        backend = create_provider("openai", model="gpt-4o-mini")

    config = Config(agents=3, rounds=1, concurrency=3)

    task = (
        "What are the top 3 architectural principles for designing resilient "
        "cloud applications on AWS? Provide concrete examples."
    )

    print(">>> Starting Swarmmy with OpenAI (gpt-4o-mini)...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} calls.")


if __name__ == "__main__":
    main()
