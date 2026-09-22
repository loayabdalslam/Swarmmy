"""
DeepSeek: Quickstart Swarm with DeepSeek-V3
===========================================
Demonstrates running a swarm with DeepSeek's flagship model `deepseek-chat` (V3).

Setup:
  1. Get an API key at https://platform.deepseek.com/
  2. In PowerShell: $env:DEEPSEEK_API_KEY="sk-..."
  3. Run: python examples/deepseek/01_deepseek_v3_swarm.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("[WARN] DEEPSEEK_API_KEY not found in environment.")
        print("       Set it via: $env:DEEPSEEK_API_KEY=\"sk-...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: DeepSeek-V3 analyzed and resolved the concurrency bottleneck."
    else:
        # Default model is deepseek-chat (V3)
        backend = create_provider("deepseek")

    config = Config(agents=3, rounds=1, concurrency=3)

    task = (
        "Analyze how the Python GIL removal (PEP 703, free-threaded Python 3.13) "
        "impacts multi-threaded network IO vs CPU-bound multiprocessing."
    )

    print(">>> Starting Swarmmy with DeepSeek-V3...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} calls.")


if __name__ == "__main__":
    main()
