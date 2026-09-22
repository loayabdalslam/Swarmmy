"""
OpenAI: Distributed System Design Swarm
=======================================
Demonstrates using OpenAI with specialized architecture roles.
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[WARN] OPENAI_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Utilize consistent hashing with virtual nodes and Dynamo-style replication."
    else:
        backend = create_provider("openai", model="gpt-4o-mini")

    architecture_roles = [
        "Database Sharding Lead: Focus on partition keys, hot-spot avoidance, and resharding strategies.",
        "Caching & Latency Engineer: Focus on Redis clustering, cache stampede prevention, and TTL policies.",
        "Consensus & Replication Architect: Focus on Raft/Paxos consensus, quorum reads/writes, and split-brain recovery."
    ]

    config = Config(agents=3, rounds=1, roles=architecture_roles, live=True)

    task = "Design a globally distributed key-value store capable of handling 100,000 writes/second with strong consistency guarantees."

    result = run_sync(task, backend=backend, config=config)

    print("\n" + "=" * 70)
    print("📐 DISTRIBUTED SYSTEM DESIGN:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
