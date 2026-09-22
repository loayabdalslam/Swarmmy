# 🤗 Hugging Face Provider Guide & Examples (Local GPU & Serverless)

Swarmmy offers first-class support for Hugging Face models in two distinct execution modes:
1. **Local GPU Inference (`provider="hf"` or `"huggingface"`)**: Loads open-source weights directly into your PyTorch CUDA device.
2. **Serverless Inference API (`provider="hf-api"`)**: Queries models hosted on Hugging Face's cloud infrastructure via HTTP token.

---

## 🚀 1. Local GPU Execution (`provider="hf"`)

### Prerequisites & Installation
Local GPU execution requires PyTorch, Transformers, and Accelerate:
```bash
pip install 'swarmmy[hf]'
```
Or manually:
```bash
pip install torch transformers accelerate
```

### Key Architectural Advantage in Swarmmy
When multiple agents run in a swarm concurrently, naive frameworks can cause sudden GPU Out-Of-Memory (OOM) crashes by running multiple forward passes at once.

**Swarmmy solves this natively**:
- It features **serialized generation locks** with thread pools.
- Concurrent agents prepare prompts asynchronously, but GPU model forward passes are serialized under `torch.inference_mode()`, preventing VRAM spikes while maintaining optimal throughput.
- Supports `device_map="auto"` for multi-GPU or CPU-offloaded inference.

### Code Example (< 600M Instruct Model):
```python
from swarmmy import Config, create_provider, run_sync

# Automatically uses CUDA / device_map="auto" with a fast <600M model
backend = create_provider(
    "hf",
    model="Qwen/Qwen2.5-0.5B-Instruct",  # 490M parameters (< 600M)
    device_map="auto",
    context_tokens=4096
)

result = run_sync(
    "Design a thread-safe singleton pattern in modern C++.",
    backend=backend,
    config=Config(agents=2, rounds=1),
    live=True
)
print(result.answer)
```

---

## ☁️ 2. Serverless Inference API (`provider="hf-api"`)

If you don't have a local GPU, you can use Hugging Face's Serverless Inference API:

### API Key Setup
1. Go to **[Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens)**.
2. Create a User Access Token with `read` permissions.
3. Set your token:
   - **PowerShell**: `$env:HF_TOKEN="hf_YourTokenHere..."`
   - **Bash**: `export HF_TOKEN="hf_YourTokenHere..."`
   - **.env**: `HF_TOKEN=hf_YourTokenHere...`

### Code Example:
```python
from swarmmy import create_provider

backend = create_provider(
    "hf-api",
    model="meta-llama/Llama-3.3-70B-Instruct"
)
```

---

## ⚙️ Recommended Local Models for GPU

### Compact Instruct Models (< 600M Parameters)
| Model | Parameters | Download Size | Est. VRAM | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| `Qwen/Qwen2.5-0.5B-Instruct` | **490M** (< 600M) | ~980 MB | ~1.2 GB | **Default**. SOTA sub-1B instruct & coding |
| `HuggingFaceTB/SmolLM2-360M-Instruct` | **360M** (< 600M) | ~720 MB | ~800 MB | Ultra-compact local reasoning |
| `HuggingFaceTB/SmolLM2-135M-Instruct` | **135M** (< 600M) | ~270 MB | ~400 MB | Instant testing & embedded devices |

### Mid-Range & Large Models (> 1B Parameters)
| Model | Parameters | Est. VRAM | Best Used For |
| :--- | :--- | :--- | :--- |
| `microsoft/Phi-3.5-mini-instruct` | 3.8B | ~8 GB | Excellent balanced reasoning |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | 7.6B | ~14 GB | Flagship local code & architecture design |

---

## 📁 Examples in this Directory

1. **[`01_local_gpu_quickstart.py`](01_local_gpu_quickstart.py)**: Running local Hugging Face CausalLM on PyTorch CUDA with automatic GPU memory safety.
2. **[`02_serverless_api_hf.py`](02_serverless_api_hf.py)**: Running via Hugging Face's cloud Serverless Inference API with `HF_TOKEN`.
