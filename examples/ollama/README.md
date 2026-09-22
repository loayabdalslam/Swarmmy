# 🦙 Ollama Provider Guide & Examples (100% Offline & Private)

Ollama allows running cutting-edge open-weight models (Llama 3, DeepSeek-R1, Qwen 2.5 Coder, Mistral) locally on your own GPU/CPU.

### Why use Ollama with Swarmmy?
- **Zero API Keys Required**: No signups, no subscriptions, no credit cards.
- **100% Data Privacy**: No proprietary code, prompts, or proprietary data ever leaves your computer.
- **Zero Cost**: Run as many agents, rounds, and experiments as you want completely free.

---

## 🚀 3-Step Setup Guide

### Step 1: Install Ollama
Download and install Ollama from **[ollama.com](https://ollama.com)** (available for Windows, macOS, and Linux).

### Step 2: Download Your Preferred Model
Open your terminal (PowerShell, Command Prompt, or Bash) and pull a model:
```bash
# General purpose / coding (Recommended):
ollama run llama3:latest

# Or deep reasoning:
ollama run deepseek-r1:8b

# Or coding specialist:
ollama run qwen2.5-coder:7b
```

### Step 3: Run Swarmmy
Swarmmy automatically connects to `http://localhost:11434/v1` by default!

```bash
swarmmy "Explain atomic operations" --provider ollama --live
```

---

## 💻 Python Usage

```python
from swarmmy import create_provider, Config, run_sync

# Automatically connects to your local Ollama instance
backend = create_provider("ollama", model="llama3:latest")

result = run_sync(
    "How does consistent hashing prevent data imbalance?",
    backend=backend,
    config=Config(agents=3, rounds=1),
    live=True
)
print(result.answer)
```

---

## ⚙️ Hardware & Concurrency Recommendation
When running locally on consumer hardware:
- For GPUs with 8GB–16GB VRAM (RTX 3060/4060/4070), use **7B–8B models** (`llama3:latest`, `deepseek-r1:8b`).
- Keep `concurrency=2` or `concurrency=1` in `Config` so your GPU processes requests sequentially without VRAM thrashing.

---

## 📁 Examples in this Directory

1. **[`01_local_offline_quickstart.py`](01_local_offline_quickstart.py)**: Running your first 100% offline swarm with local Llama 3.
2. **[`02_private_refactor_ollama.py`](02_private_refactor_ollama.py)**: Refactoring private proprietary legacy code with zero external network leakage.
