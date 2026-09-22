"""
Groq: Creative Brainstorming Swarm (roles="creative")
=====================================================
Demonstrates using Groq with the built-in creative personas
to rapidly brainstorm product names and taglines.
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[WARN] GROQ_API_KEY not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Brand Name = 'FlowScale' - Tagline: 'Distributed state made effortless.'"
    else:
        backend = create_provider("groq", model="llama-3.3-70b-versatile")

    # Built-in creative preset
    config = Config(agents=3, rounds=1, roles="creative", concurrency=3)

    task = (
        "Brainstorm 3 memorable names and taglines for an open-source "
        "distributed key-value database built for extreme write throughput."
    )

    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("💡 CREATIVE BRAINSTORMING RESULTS:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
