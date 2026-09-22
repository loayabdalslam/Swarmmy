"""
DeepSeek: Deep Chain-of-Thought Swarm with DeepSeek-R1
======================================================
Demonstrates using DeepSeek's reasoning model `deepseek-reasoner` (R1)
for mathematically rigorous, multi-agent algorithmic deliberation.
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("[WARN] DEEPSEEK_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: DeepSeek-R1 mathematical proof verified under worst-case asymptotic bounds."
    else:
        # Use DeepSeek-R1 reasoning model
        backend = create_provider("deepseek", model="deepseek-reasoner")

    math_roles = [
        "Computational Complexity Theorist: Focus on asymptotic time/space bounds O(N) and proof correctness.",
        "Applied Algorithmic Engineer: Focus on cache locality, CPU branch prediction, and SIMD vectorization.",
        "Edge-Case Adversary: Focus on integer overflows, degenerate inputs, and off-by-one errors."
    ]

    config = Config(agents=3, rounds=1, roles=math_roles, live=True)

    task = (
        "Design a lock-free concurrent ring buffer queue in C++20. "
        "Formulate formal proofs for memory ordering (std::memory_order_acquire / release) "
        "and verify absence of ABA problems."
    )

    print(">>> Starting DeepSeek-R1 Reasoning Swarm...")
    result = run_sync(task, backend=backend, config=config)

    print("\n" + "=" * 70)
    print("🧠 DEEPSEEK-R1 REASONING SYNTHESIS:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
