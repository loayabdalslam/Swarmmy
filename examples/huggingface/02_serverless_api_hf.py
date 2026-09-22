"""
Hugging Face: Serverless Inference API Swarm
=============================================
Demonstrates running a swarm via Hugging Face's cloud Serverless API
using your personal HF User Access Token.

Setup:
  1. Get token at https://huggingface.co/settings/tokens
  2. In PowerShell: $env:HF_TOKEN="hf_..."
  3. Run: python examples/huggingface/02_serverless_api_hf.py
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

    if not token:
        print("[WARN] HF_TOKEN not found in environment.")
        print("       Set it via: $env:HF_TOKEN=\"hf_...\"")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Hugging Face serverless API swarm completed task."
    else:
        # Connect to HF Serverless Inference API
        backend = create_provider(
            "hf-api",
            model="meta-llama/Llama-3.3-70B-Instruct",
            api_key=token,
        )

    config = Config(agents=3, rounds=1, concurrency=3)

    task = (
        "Explain the memory hierarchy in modern GPU architectures (HBM3e, L2 cache, SRAM register file) "
        "and how FlashAttention utilizes SRAM to avoid HBM memory bandwidth bottlenecks."
    )

    print(">>> Starting Swarmmy with Hugging Face Serverless API...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
