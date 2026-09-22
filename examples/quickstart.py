"""Quickstart example for Swarmmy."""

from swarmmy import Config, OpenAICompatible, Swarm, run_sync

# Option 1: Asynchronous usage
import asyncio

async def async_main():
    backend = OpenAICompatible(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url="http://localhost:8000/v1",
        api_key="",  # Or set SWARM_API_KEY environment variable
    )
    swarm = Swarm(backend=backend, config=Config(agents=4, rounds=1))
    
    result = await swarm.run("Design an efficient rate limiting algorithm and analyze its edge cases.")
    print("--- Swarm Answer ---")
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} model calls.")


# Option 2: Synchronous one-liner
def sync_main():
    backend = OpenAICompatible(model="gpt-4o-mini", base_url="https://api.openai.com/v1")
    result = run_sync(
        "Compare event-driven architecture vs monolithic architectures.",
        backend=backend,
        config=Config(agents=3, rounds=1),
    )
    print(result.answer)


if __name__ == "__main__":
    # Run async example
    asyncio.run(async_main())
