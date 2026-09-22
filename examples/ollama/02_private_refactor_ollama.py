"""
Ollama: Private Code Refactoring Swarm (Zero Cloud Egress)
===========================================================
Demonstrates using local offline Ollama models to refactor sensitive
proprietary code without exposing any data to third-party cloud APIs.
"""

import json
import urllib.request
from swarmmy import Config, create_provider, run_sync


def get_available_ollama_model() -> str | None:
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            return models[0] if models else None
    except Exception:
        return None


def main():
    installed_model = get_available_ollama_model()
    if installed_model:
        print(f"[INFO] Using local Ollama model: '{installed_model}'")
        backend = create_provider("ollama", model=installed_model)
    else:
        print("[NOTICE] Ollama not running or model not found. Running in simulation mode.")
        def backend(messages, **kwargs):
            return "Consensus: Refactored legacy monolithic module into asynchronous transactional outbox."

    roles = [
        "Legacy Code Auditor: Identify tight coupling and database connection leaks.",
        "Event-Driven Architect: Deconstruct synchronous calls into durable queue messages.",
    ]

    config = Config(agents=2, rounds=1, roles=roles, concurrency=2, live=True)

    task = (
        "Refactor a legacy synchronous billing module into an asynchronous event-driven worker. "
        "Eliminate global database state, add idempotency keys, and handle transient payment failures."
    )

    result = run_sync(task, backend=backend, config=config)

    print("\n" + "=" * 70)
    print("🔒 REFACTORED CODE (100% PRIVATE):")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
