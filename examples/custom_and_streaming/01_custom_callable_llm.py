"""
Custom Backend: Connecting Any Function or LiteLLM to Swarmmy
============================================================
Demonstrates wrapping any Python function as a Swarmmy provider.
"""

from swarmmy import CallableProvider, Config, Swarm


def my_custom_llm(messages, temperature=0.7, max_tokens=1024):
    """Can call LiteLLM, a local PyTorch pipeline, vLLM, or proprietary enterprise APIs."""
    user_prompt = messages[0]["content"]
    
    # Handle swarm peer review requests
    if "Evaluate each peer solution" in user_prompt:
        import json
        data = json.loads(user_prompt[user_prompt.index('{"task"'):])
        return json.dumps([
            {"id": cand["id"], "score": 0.90, "critique": "Solid logic and modular design."}
            for cand in data["material"]
        ])
    
    return "Custom Provider Result: Proposed a modular service mesh with mTLS encryption."


def main():
    config = Config(agents=3, rounds=1, concurrency=3)
    swarm = Swarm(backend=my_custom_llm, config=config)

    print(">>> Starting Swarmmy with Custom Function Backend...")
    result = swarm.run_sync("Design a zero-trust service mesh architecture.")

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)
    print(f"\nCalls: {result.calls} | Time: {result.elapsed_seconds:.3f}s")


if __name__ == "__main__":
    main()
