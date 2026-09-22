"""
Ollama: 100% Offline Quickstart Swarm
======================================
Demonstrates running a swarm completely offline on local hardware with Ollama.
Zero cloud costs, zero data egress, zero API keys required!

Prerequisites:
  1. Download and install Ollama: https://ollama.com
  2. Pull a model (e.g. `ollama run llama3:latest` or `ollama run gemma3:4b`)
  3. Run: python examples/ollama/01_local_offline_quickstart.py
"""

import json
import urllib.request
from swarmmy import Config, create_provider, run_sync


def get_available_ollama_model() -> str | None:
    """Queries local Ollama to discover currently installed models."""
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
        print(f"[INFO] Connected to local Ollama at http://127.0.0.1:11434")
        print(f"[INFO] Using detected installed model: '{installed_model}'")
        backend = create_provider("ollama", model=installed_model)
    else:
        print("[NOTICE] Local Ollama is offline or no models are downloaded.")
        print("         Running in simulated offline demo mode.")
        print("         To use real local models: install Ollama from https://ollama.com\n")
        def backend(messages, **kwargs):
            return "Consensus: Local offline swarm completed deliberation on local hardware."

    # Keep concurrency moderate (e.g. 2) to be gentle on local consumer GPU VRAM
    config = Config(agents=2, rounds=1, concurrency=2)

    task = (
        "Explain the key architectural differences between Raft and Paxos consensus algorithms, "
        "specifically leader election and log replication."
    )

    print(">>> Starting Offline Swarmmy with Ollama...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🔒 FINAL OFFLINE CONSENSUS ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCompleted in {result.elapsed_seconds:.2f}s using {result.calls} calls.")


if __name__ == "__main__":
    main()
