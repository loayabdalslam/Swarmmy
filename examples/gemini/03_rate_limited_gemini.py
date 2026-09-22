"""
Google Gemini: Rate-Limited Free Tier (15 RPM) & Budget Protection
==================================================================
Demonstrates how to safely use Gemini's free tier without triggering
HTTP 429 Too Many Requests, by attaching UsageLimits with RPM throttling.
"""

import os
from swarmmy import Config, UsageLimits, create_provider, run_sync


def main():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Edge computing improves localized response latency."
    else:
        backend = create_provider("gemini", model="gemini-2.0-flash")

    # Free tier safe configuration: max 15 requests/minute
    limits = UsageLimits(
        rpm=15,                    # Automatic client-side rate limiting
        max_total_tokens=25_000,   # Prevent unbounded token usage
        max_cost_usd=0.05,         # Hard financial budget ceiling
        max_retries=3,             # Retry on rate limit with exponential backoff
    )

    config = Config(
        agents=3,
        rounds=1,
        limits=limits,
    )

    task = "Analyze the benefits and challenges of deploying machine learning models at the edge."

    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)

    # Print usage report
    report = result.usage
    print("\n" + "=" * 70)
    print("📊 USAGE REPORT:")
    print("=" * 70)
    print(f"• Total Tokens       : {report.total_tokens}")
    print(f"• Estimated Cost USD : ${report.estimated_cost_usd:.5f}")
    print(f"• Throttling Waits   : {report.rate_limit_waits_seconds:.2f}s")


if __name__ == "__main__":
    main()
