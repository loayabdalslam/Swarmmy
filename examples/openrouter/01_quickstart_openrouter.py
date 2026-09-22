"""
OpenRouter: Multi-Model Gateway Swarm
=====================================
Demonstrates running a swarm using OpenRouter to access 200+ models.

Setup:
  1. In PowerShell: $env:OPENROUTER_API_KEY="sk-or-v1-..."
  2. Run: python examples/openrouter/01_quickstart_openrouter.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        print("[WARN] OPENROUTER_API_KEY not found in environment.")
        print("       Set it via: $env:OPENROUTER_API_KEY=\"sk-or-v1-...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: OpenRouter gateway routed and resolved swarm task."
    else:
        # Default model is meta-llama/llama-3.3-70b-instruct
        backend = create_provider(
            "openrouter",
            model="meta-llama/llama-3.3-70b-instruct"
        )

    config = Config(agents=3, rounds=1, concurrency=3)

    task = "Compare WebSockets vs HTTP Server-Sent Events (SSE) for low-latency live financial dashboards."

    print(">>> Starting Swarmmy with OpenRouter...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
