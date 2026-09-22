"""
Lifecycle Event Hooks & Telemetry Tracing
==========================================
Demonstrates attaching custom event hooks (`on_event`) to track Swarmmy's
lifecycle events (proposals, reviews, revisions, synthesis) for monitoring,
telemetry, or custom terminal logs.
"""

from swarmmy import Config, Swarm, TraceEvent


def mock_llm(messages, **kwargs):
    return "Consensus: Event-driven tracking validated across all agents."


def on_lifecycle_event(event: TraceEvent):
    status = "SUCCESS" if event.ok else "FAILED"
    agent_name = f"Agent {event.agent}" if event.agent >= 0 else "Consensus"
    print(f"[{status}] Stage: {event.stage.upper():<10} | {agent_name:<10} | Latency: {event.seconds:.4f}s")


def main():
    config = Config(agents=3, rounds=1)
    swarm = Swarm(backend=mock_llm, config=config, on_event=on_lifecycle_event)

    print(">>> Executing Swarmmy with Custom Lifecycle Listener...")
    result = swarm.run_sync("Formulate telemetry metrics for tracking agent latency.")

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nTotal Traced Events: {len(result.trace)}")


if __name__ == "__main__":
    main()
