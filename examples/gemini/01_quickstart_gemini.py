"""
Google Gemini: Quickstart Swarm Execution
========================================
Demonstrates running a bounded peer-review swarm with Google Gemini.

Setup:
  1. Get a free API key at https://aistudio.google.com/
  2. In PowerShell: $env:GEMINI_API_KEY="AIzaSy..."
  3. Run: python examples/gemini/01_quickstart_gemini.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("[WARN] GEMINI_API_KEY not found in environment.")
        print("       Set it via: $env:GEMINI_API_KEY=\"your_key_here\" (PowerShell)")
        print("       Running in mock demo mode for demonstration...\n")
        # Provide a quick mock so the script doesn't crash
        def backend(messages, **kwargs):
            return "Consensus response: Google Gemini swarm completed deliberation."
    else:
        # Connect to Google Gemini using default gemini-2.0-flash
        backend = create_provider("gemini", model="gemini-2.0-flash")

    # 3 peer agents, 1 round of cross peer review
    config = Config(
        agents=3,
        rounds=1,
        concurrency=3,
    )

    task = (
        "Explain the core engineering differences between monolithic architectures "
        "and microservices, highlighting database consistency trade-offs."
    )

    print(">>> Starting Swarmmy with Google Gemini...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL CONSENSUS ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} API calls.")


if __name__ == "__main__":
    main()
