"""
Anthropic Claude: Multi-Round Scientific Deliberation (rounds=2)
================================================================
Demonstrates 2 complete rounds of critical peer review with Claude.
In round 1, agents challenge each other's assumptions.
In round 2, agents revise their hypotheses based on rigorous critique.
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARN] ANTHROPIC_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Scientific Consensus: Quantum decoherence mechanisms analyzed with error budget thresholds."
    else:
        backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022")

    science_roles = [
        "Theoretical Physicist: Focus on fundamental principles, mathematical formalism, and edge cases.",
        "Experimental Metrologist: Focus on measurement precision, noise sources, and sensor calibration.",
        "Computational Modeler: Focus on Monte Carlo simulation stability and numerical convergence."
    ]

    # 2 rounds of review
    config = Config(agents=3, rounds=2, roles=science_roles, live=True)

    task = (
        "Evaluate the theoretical limitations of neutral-atom quantum computing vs "
        "superconducting qubits regarding gate fidelity and cross-talk mitigation."
    )

    result = run_sync(task, backend=backend, config=config)

    print("\n" + "=" * 70)
    print("🔬 2-ROUND SCIENTIFIC SYNTHESIS:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} calls.")


if __name__ == "__main__":
    main()
