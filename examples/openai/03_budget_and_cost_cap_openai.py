"""
OpenAI: Hard Budget Caps & Financial Ceilings
============================================
Demonstrates strictly capping OpenAI API costs in USD and tokens.
If the budget cap is reached, Swarmmy terminates gracefully without runaway spending.
"""

import os
from swarmmy import Config, UsageLimits, create_provider, run_sync


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[WARN] OPENAI_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Micro-frontend architecture enables decoupled deployment."
    else:
        backend = create_provider("openai", model="gpt-4o-mini")

    # Hard ceiling of $0.05 USD and 30,000 tokens
    limits = UsageLimits(
        max_cost_usd=0.05,        # Stated in US Dollars
        max_total_tokens=30_000,  # Prompt + Completion tokens
        rpm=60,                   # Rate limit throttling
    )

    config = Config(agents=3, rounds=1, limits=limits)

    task = "Compare micro-frontend architectures with monolithic frontend architectures for enterprise teams."

    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 RESULT:")
    print("=" * 70)
    print(result.answer)

    print("\n" + "=" * 70)
    print("💰 FINANCIAL AUDIT:")
    print("=" * 70)
    print(f"• Total Tokens       : {result.usage.total_tokens:,}")
    print(f"• Estimated Cost     : ${result.usage.estimated_cost_usd:.5f} USD")
    print(f"• Budget Ceiling     : ${limits.max_cost_usd:.2f} USD")


if __name__ == "__main__":
    main()
