"""
Hugging Face: Lightweight Local GPU Swarm (< 600M Instruct Model)
==================================================================
Demonstrates running a swarm on your local GPU (CUDA / PyTorch) using an
ultra-compact Instruct model under 600M parameters:

Default Model:
  • `Qwen/Qwen2.5-0.5B-Instruct` (~490 Million parameters < 600M)
    - Download size: ~980 MB (fp16)
    - VRAM usage: ~1.2 GB
    - State-of-the-art instruction following for sub-1B models.

Alternative < 600M models:
  • `HuggingFaceTB/SmolLM2-360M-Instruct` (360M parameters)
  • `HuggingFaceTB/SmolLM2-135M-Instruct` (135M parameters)

Swarmmy GPU Features:
  • Automatic `device_map="auto"` (CUDA GPU acceleration).
  • Thread-safe generation lock prevents GPU Out-Of-Memory (OOM) spikes
    when multiple swarm agents execute concurrently.

Prerequisites:
  pip install 'swarmmy[hf]'
  (Requires: torch, transformers, accelerate)
"""

import os
import sys
from swarmmy import Config, create_provider, run_sync


# Compact Instruct model under 600M parameters
DEFAULT_INSTRUCT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"  # 490M params (< 600M)
ALTERNATIVE_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"  # 360M params (< 600M)


def main():
    # Allow overriding via environment variable if desired
    model_name = os.environ.get("HF_LOCAL_MODEL", DEFAULT_INSTRUCT_MODEL)

    print("=" * 75)
    print(">>> SWARMMY: LOCAL GPU INFERENCE (< 600M INSTRUCT MODEL) <<<")
    print("=" * 75)
    print(f"• Target Model    : {model_name}")
    print(f"• Parameter Count : ~490M parameters (Under 600M)")
    print(f"• Acceleration    : PyTorch CUDA / device_map='auto'")
    print("-" * 75)

    try:
        import torch
        cuda_status = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda_status else "CPU (CUDA not detected)"
        print(f"[INFO] Hardware detected: {gpu_name}")

        print(f"[INFO] Loading '{model_name}' weights onto GPU (device_map='auto')...")
        backend = create_provider(
            "hf",
            model=model_name,
            device_map="auto",
            context_tokens=4096,
        )
        print("[INFO] Model loaded successfully into GPU VRAM!\n")

    except ImportError:
        print("[WARN] 'torch' or 'transformers' not installed.")
        print("       Install with: pip install 'swarmmy[hf]'")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Sub-600M local GPU model completed swarm deliberation."

    except Exception as e:
        print(f"[WARN] Could not load model from Hugging Face: {e}")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Sub-600M local GPU model completed swarm deliberation."

    # 2 peer agents, 1 review round, concurrency=2 for gentle GPU memory usage
    config = Config(
        agents=2,
        rounds=1,
        concurrency=2,
        max_tokens=350,  # Fast generation on lightweight models
    )

    task = (
        "Explain the single most important rule for avoiding deadlocks in concurrent "
        "programming, with a short Python code example using threading.Lock."
    )

    print(">>> Launching bounded peer-review swarm on local GPU...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 75)
    print("🏆 FINAL CONSENSUS (GENERATED ON LOCAL GPU):")
    print("=" * 75)
    print(result.answer)
    print("-" * 75)
    print(f"• Total Model Inferences : {result.calls}")
    print(f"• Total Execution Time   : {result.elapsed_seconds:.2f} seconds")
    print("=" * 75)


if __name__ == "__main__":
    main()
