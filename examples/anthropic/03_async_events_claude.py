"""
Anthropic Claude: Asynchronous Swarm with Event Hooks
=====================================================
Demonstrates running Claude within an asynchronous event loop (asyncio)
and attaching a custom event callback `on_event` to monitor each stage.
"""

import asyncio
import os
from swarmmy import Config, Swarm, TraceEvent, create_provider


async def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARN] ANTHROPIC_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Zero-trust architecture enforced across all micro-perimeters."
    else:
        backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022")

    # Custom progress event handler
    def handle_event(event: TraceEvent):
        icon = "🟢" if event.ok else "🔴"
        agent = f"Agent {event.agent}" if event.agent >= 0 else "Consensus"
        print(f"[{icon}] Stage: {event.stage.upper():<10} | {agent:<11} | Duration: {event.seconds:.3f}s")

    config = Config(agents=3, rounds=1, concurrency=3)
    swarm = Swarm(backend=backend, config=config, on_event=handle_event)

    task = "Design a zero-trust network segmentation plan for a hybrid enterprise cloud."

    print(">>> Starting Async Swarm with Claude...")
    result = await swarm.run(task)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    asyncio.run(main())
