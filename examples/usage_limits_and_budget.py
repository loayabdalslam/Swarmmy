"""Example demonstrating usage limits, RPM throttling, and token/cost budgets."""

import asyncio
import json
from swarmmy import (
    Config,
    Swarm,
    UsageLimits,
    create_provider,
    run_sync,
)


def mock_ai_service(messages, temperature=0.7, max_tokens=1024):
    """Simulated LLM service."""
    p = messages[0]["content"]
    if p.startswith("Evaluate"):
        data = json.loads(p[p.index('{"task"'):])
        return json.dumps([
            {"id": x["id"], "score": 0.88, "critique": "Solid rationale."}
            for x in data["material"]
        ])
    return (
        "Proposed Solution: Design a zero-trust multi-region architecture "
        "using mTLS and distributed session tokens."
    )


def main():
    print("=== Swarmmy Usage Limits & Budget Demo ===\n")

    # 1. Define explicit usage limits
    limits = UsageLimits(
        rpm=30,                   # Throttles execution to max 30 requests per minute
        max_total_tokens=25_000,  # Hard ceiling: aborts if tokens exceed 25k
        max_cost_usd=0.05,        # Hard ceiling: aborts if estimated cost exceeds $0.05 USD
        max_retries=3,            # Automatically retries if provider returns HTTP 429
    )

    config = Config(
        agents=3,
        rounds=1,
        concurrency=2,
        limits=limits,
    )

    print("Running swarm with usage limits:")
    print(f"  - Max RPM:          {config._resolved_limits.rpm}")
    print(f"  - Max Total Tokens: {config._resolved_limits.max_total_tokens}")
    print(f"  - Max Cost USD:     ${config._resolved_limits.max_cost_usd}")
    print(f"  - Max Retries:      {config._resolved_limits.max_retries}\n")

    result = run_sync(
        "Design a secure, multi-region database replication strategy.",
        backend=mock_ai_service,
        config=config,
    )

    print("--- Swarm Execution Completed ---")
    print(result.answer)
    print("\n--- Usage Report ---")
    report = result.usage
    print(f"Total Model Calls:     {result.calls}")
    print(f"Prompt Tokens:         {report.prompt_tokens}")
    print(f"Completion Tokens:     {report.completion_tokens}")
    print(f"Total Tokens:          {report.total_tokens}")
    print(f"Estimated Cost:        ${report.estimated_cost_usd:.6f} USD")
    print(f"Throttling Wait Time:  {report.rate_limit_waits_seconds:.2f}s")
    print(f"Retries Attempted:     {report.retries_attempted}")


if __name__ == "__main__":
    main()
