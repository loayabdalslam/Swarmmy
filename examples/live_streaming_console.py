"""Live demonstration of real-time rich colored console output in Swarmmy."""

import asyncio
import json
import time

from swarmmy import Config, Swarm, run_sync


def mock_smart_agent(messages, temperature=0.7, max_tokens=1024):
    """Simulated fast multi-agent reasoning for live visual demonstration."""
    time.sleep(0.4)  # Small delay to simulate inference time
    prompt = messages[0]["content"]

    if prompt.startswith("Evaluate"):
        data = json.loads(prompt[prompt.index('{"task"'):])
        return json.dumps([
            {
                "id": cand["id"],
                "score": 0.82 + (cand["id"] * 0.05),
                "critique": f"Candidate {cand['id']} provides robust architecture, but needs telemetry.",
            }
            for cand in data["material"]
        ])

    if "Improve your solution" in prompt:
        return (
            "Revised Proposal: Incorporated distributed rate-limiting and added "
            "Prometheus metrics with circuit-breakers for fault isolation."
        )

    if "Produce the best final answer" in prompt:
        return (
            "Synthesized Unified Architecture:\n"
            "1. Core: Token bucket algorithm with Redis Cluster for distributed sync.\n"
            "2. Edge: Local in-memory leaky bucket cache to shield database from spike traffic.\n"
            "3. Reliability: Circuit breaker mechanism with fallback rate limits.\n"
            "4. Observability: OpenTelemetry tracing and Prometheus metrics."
        )

    # Initial proposal
    return (
        "Initial Solution: Implement sliding-window counter algorithm with memcached "
        "and active replication across availability zones."
    )


def main():
    print("Initializing Swarmmy with live real-time colored printer...\n")

    # Run Swarm with live=True for real-time rich colored cards
    config = Config(
        agents=3,
        rounds=1,
        concurrency=3,
        roles=[
            "Focus on high throughput and low latency under peak load.",
            "Focus on high availability, network partition tolerance, and failover.",
            "Focus on monitoring, telemetry, and rate limit telemetry.",
        ],
    )

    result = run_sync(
        "Design a distributed rate limiter supporting 100k requests/sec.",
        backend=mock_smart_agent,
        config=config,
        live=True,  # Enables real-time synchronized colored output!
    )

    print("\n" + "=" * 70)
    print("FINAL RESULT SUMMARY:")
    print("=" * 70)
    print(f"Total API Calls: {result.calls}")
    print(f"Total Elapsed:   {result.elapsed_seconds:.2f}s")
    print(f"Warnings:        {len(result.warnings)}")


if __name__ == "__main__":
    main()
