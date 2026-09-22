"""
FastAPI Server-Sent Events (SSE) Swarm Streaming
=================================================
Demonstrates using Swarmmy's built-in StreamTunnel to stream real-time
agent deliberation events over standard HTTP Server-Sent Events (SSE).
"""

import asyncio
import json
from swarmmy import (
    Config,
    StreamTunnel,
    Swarm,
)


def mock_backend(messages, temperature=0.7, max_tokens=1024):
    p = messages[0]["content"]
    if "Evaluate each peer solution" in p:
        data = json.loads(p[p.index('{"task"'):])
        return json.dumps([
            {"id": x["id"], "score": 0.88, "critique": f"Solid reasoning for Candidate {x['id']}."}
            for x in data["material"]
        ])
    return "Microservice proposal with event sourcing and CQRS pattern."


async def demonstrate_tunnel_consumption():
    """Simulates how a Web API (like FastAPI or Flask) streams events live to an HTTP client."""
    print("=== Simulating API SSE Streaming with StreamTunnel ===\n")

    # 1. Create the tunnel
    tunnel = StreamTunnel()

    # 2. Configure Swarm
    config = Config(agents=3, rounds=1, concurrency=3)
    swarm = Swarm(backend=mock_backend, config=config, tunnel=tunnel)

    # 3. Launch swarm in background task (just like inside a FastAPI route handler)
    swarm_task = asyncio.create_task(
        swarm.run("Design an event-driven payment processing architecture.")
    )

    # 4. Stream events to client as they arrive in real-time
    print("Client connected to SSE stream... Listening to incoming events:")
    step_count = 0
    async for sse_chunk in tunnel.sse_stream():
        step_count += 1
        lines = sse_chunk.strip().split("\n")
        first_line = lines[0] if lines else ""
        data_line = lines[1] if len(lines) > 1 else ""
        print(f"  [SSE Event #{step_count:<2}] {first_line} | {data_line[:80]}...")

    result = await swarm_task
    print("\n--- Swarm Finished Successfully ---")
    print(f"Final Answer Length: {len(result.answer)} characters")
    print(f"Total Streamed Events: {step_count}")


if __name__ == "__main__":
    asyncio.run(demonstrate_tunnel_consumption())
