# 🔀 OpenRouter Provider Guide & Examples

OpenRouter provides a unified API gateway to over 200+ AI models across dozens of model providers (Anthropic, OpenAI, Meta, Google, Mistral, DeepSeek, Qwen) with a single API key and shared credit balance.

---

## 🔑 How to Get and Set Up Your OpenRouter API Key

### 1. Obtain an API Key
1. Go to **[OpenRouter Keys](https://openrouter.ai/keys)**.
2. Sign in and create a key (`sk-or-v1-...`).

---

### 2. How to Set Your API Key

- **Windows PowerShell**:
  ```powershell
  $env:OPENROUTER_API_KEY="sk-or-v1-YourKeyHere..."
  ```
- **Bash / macOS**:
  ```bash
  export OPENROUTER_API_KEY="sk-or-v1-YourKeyHere..."
  ```
- **.env file**:
  ```env
  OPENROUTER_API_KEY=sk-or-v1-YourKeyHere...
  ```

---

## 📁 Examples in this Directory

- **[`01_quickstart_openrouter.py`](01_quickstart_openrouter.py)**: Running swarms with open models via OpenRouter (e.g., `meta-llama/llama-3.3-70b-instruct`).
