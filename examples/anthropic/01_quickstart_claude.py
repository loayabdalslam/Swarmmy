"""
Anthropic Claude: Quickstart Swarm Deliberation
==============================================
Demonstrates standard swarm execution with Claude 3.5 Sonnet.

Setup:
  1. In PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
  2. Run: python examples/anthropic/01_quickstart_claude.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARN] ANTHROPIC_API_KEY not found in environment.")
        print("       Set it via: $env:ANTHROPIC_API_KEY=\"sk-ant-...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Claude swarm delivered nuanced analysis."
    else:
        backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022")

    config = Config(agents=3, rounds=1, concurrency=3)

    task = (
        "Design a robust, privacy-preserving authentication architecture using Passkeys "
        "(WebAuthn/FIDO2) for enterprise SaaS users."
    )

    print(">>> Starting Swarmmy with Anthropic Claude 3.5 Sonnet...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} calls.")


if __name__ == "__main__":
    main()
