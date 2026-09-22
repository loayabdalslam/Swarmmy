"""Example demonstrating custom agent roles and live progress event hooks."""

import asyncio
import json
from swarmmy import CallableProvider, Config, Swarm, TraceEvent


def main():
    # 1. Mock backend for demonstration
    def mock_llm(messages, temperature=0.7, max_tokens=1024):
        prompt = messages[0]["content"]
        if prompt.startswith("Evaluate"):
            data = json.loads(prompt[prompt.index('{"task"'):])
            return json.dumps([
                {"id": cand["id"], "score": 0.88, "critique": "Solid logic, good focus on safety."}
                for cand in data["material"]
            ])
        return (
            "Proposed solution: implement a distributed token-bucket filter "
            "with Redis cluster backing."
        )

    # 2. Live progress event listener
    def on_progress(event: TraceEvent):
        status = "[DONE]" if event.ok else "[FAIL]"
        print(f"{status} [{event.stage.upper():<10}] Agent {event.agent:<2} in {event.seconds:.3f}s")

    # 3. Custom roles tailored for software design
    custom_roles = [
        "Focus strictly on distributed systems consistency and network partitions.",
        "Focus on low-latency memory caching and throughput optimization.",
        "Focus on failure recovery, retries, idempotency, and circuit breakers.",
    ]

    config = Config(
        agents=3,
        rounds=1,
        roles=custom_roles,
        concurrency=3,
    )

    swarm = Swarm(
        backend=mock_llm,
        config=config,
        on_event=on_progress,
    )

    print(">>> Starting Swarmmy execution with custom roles...")
    result = swarm.run_sync("Design a distributed rate-limiting microservice.")

    print("\n" + "=" * 60)
    print("Synthesized Final Answer:")
    print("=" * 60)
    print(result.answer)
    print(f"\nTotal Calls: {result.calls} | Elapsed: {result.elapsed_seconds:.3f}s")


if __name__ == "__main__":
    main()
