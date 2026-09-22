"""
Groq: Ultra-Fast Swarm Execution (< 2 seconds)
==============================================
Demonstrates utilizing Groq's high-speed LPU inference to run an entire
multi-agent swarm with 4 agents in parallel in under 2 seconds.

Setup:
  1. Get a free API key at https://console.groq.com/
  2. In PowerShell: $env:GROQ_API_KEY="gsk_..."
  3. Run: python examples/groq/01_ultra_fast_swarm_groq.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[WARN] GROQ_API_KEY not found in environment.")
        print("       Set it via: $env:GROQ_API_KEY=\"gsk_...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Sub-second swarm completed deliberation via Groq."
    else:
        # Default model is llama-3.3-70b-versatile
        backend = create_provider("groq")

    # 4 parallel agents, 1 review round
    config = Config(agents=4, rounds=1, concurrency=4)

    task = (
        "Propose 3 distinct technical optimizations to reduce database connection "
        "pool contention under high-frequency writes."
    )

    print(">>> Starting Ultra-Fast Swarm with Groq...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("⚡ FINAL CONSENSUS (HIGH SPEED):")
    print("=" * 70)
    print(result.answer)
    print(f"\n⚡ Entire 4-agent swarm finished in only {result.elapsed_seconds:.2f}s!")


if __name__ == "__main__":
    main()
