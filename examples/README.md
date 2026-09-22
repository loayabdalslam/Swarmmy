# 🐝 Swarmmy Provider Examples & Tutorials Catalog

Welcome to the **Swarmmy Provider Examples Catalog**. Each supported LLM provider has its own dedicated directory containing standalone runnable code examples and step-by-step documentation on setting up API keys, choosing models, and handling rate limits.

---

## 🗂️ Provider Directory Matrix

| Provider Group | Identifier in `create_provider` | Default Model | Environment Variable | Key Characteristic | Directory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | `"gemini"` | `gemini-2.0-flash` | `GEMINI_API_KEY` | Generous free tier (15 RPM), ultra-fast | [`gemini/`](gemini/) |
| **OpenAI** | `"openai"` | `gpt-4o-mini` | `OPENAI_API_KEY` | Industry standard, cost-effective `gpt-4o-mini` | [`openai/`](openai/) |
| **Anthropic Claude** | `"anthropic"` | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` | SOTA reasoning, nuanced critical peer reviews | [`anthropic/`](anthropic/) |
| **Groq** | `"groq"` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | 500+ tokens/sec, full swarms in < 2s (Free tier) | [`groq/`](groq/) |
| **DeepSeek** | `"deepseek"` | `deepseek-chat` | `DEEPSEEK_API_KEY` | High reasoning at low cost (V3 & R1) | [`deepseek/`](deepseek/) |
| **Ollama** | `"ollama"` | `llama3:latest` | *None required* | **100% Offline & Private**, runs on local GPU/CPU | [`ollama/`](ollama/) |
| **Hugging Face** | `"hf"` or `"hf-api"` | Custom / Qwen / Llama | `HF_TOKEN` (API mode) | **Local GPU (PyTorch/CUDA)** or Serverless API | [`huggingface/`](huggingface/) |
| **OpenRouter** | `"openrouter"` | `meta-llama/llama-3.3-70b-instruct` | `OPENROUTER_API_KEY` | Single key access to 200+ models | [`openrouter/`](openrouter/) |
| **Mistral AI** | `"mistral"` | `mistral-large-latest` | `MISTRAL_API_KEY` | European frontier models, Codestral | [`mistral/`](mistral/) |
| **Cohere** | `"cohere"` | `command-r-plus-08-2024` | `COHERE_API_KEY` | Enterprise RAG and citations | [`cohere/`](cohere/) |
| **Azure OpenAI** | `"azure"` | Deployment-dependent | `AZURE_OPENAI_API_KEY` | Private enterprise deployments | [`azure/`](azure/) |
| **Custom & Streaming** | `"api"` / Callable | Custom | Custom | Custom Python functions, LiteLLM, FastAPI SSE | [`custom_and_streaming/`](custom_and_streaming/) |

---

## 🔑 Universal API Key Setup Guide

Swarmmy offers 4 flexible ways to configure API keys:

### 1. Environment Variables (Recommended for Production)

- **Windows PowerShell**:
  ```powershell
  # Set for current terminal session:
  $env:GEMINI_API_KEY="AIzaSy..."
  $env:OPENAI_API_KEY="sk-proj-..."
  $env:ANTHROPIC_API_KEY="sk-ant-..."
  $env:GROQ_API_KEY="gsk_..."
  $env:DEEPSEEK_API_KEY="sk-..."

  # Set permanently for your user account in Windows:
  [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSy...', 'User')
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set GEMINI_API_KEY=AIzaSy...
  set OPENAI_API_KEY=sk-proj-...
  set GROQ_API_KEY=gsk_...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export GEMINI_API_KEY="AIzaSy..."
  export OPENAI_API_KEY="sk-proj-..."
  export ANTHROPIC_API_KEY="sk-ant-..."
  export GROQ_API_KEY="gsk_..."
  ```
  *(Tip: Add export commands to your `~/.bashrc` or `~/.zshrc` file to persist them).*

---

### 2. Project `.env` File

Copy `.env.example` in the project root to `.env` and fill in the keys you plan to use:
```env
# .env
GEMINI_API_KEY=AIzaSyYourActualKeyHere
OPENAI_API_KEY=sk-proj-YourActualKeyHere
ANTHROPIC_API_KEY=sk-ant-YourActualKeyHere
GROQ_API_KEY=gsk_YourActualKeyHere
DEEPSEEK_API_KEY=sk-YourActualKeyHere
```

---

### 3. Direct Python Code Argument

You can pass the `api_key` argument directly when creating any provider:

```python
from swarmmy import create_provider

backend = create_provider("gemini", api_key="AIzaSy...")
backend = create_provider("openai", model="gpt-4o-mini", api_key="sk-proj-...")
backend = create_provider("anthropic", api_key="sk-ant-...")
backend = create_provider("groq", api_key="gsk_...")
```

---

### 4. Swarmmy Command Line Interface (CLI)

```bash
swarmmy "Your task prompt" --provider gemini --api-key "AIzaSy..." --live
```

---

## 🆓 Best Options to Get Started For Free

1. **Google Gemini (Free Tier)**:
   - Sign up at [Google AI Studio](https://aistudio.google.com/) and create a key.
   - Includes generous free quota (up to 15 RPM).
   - Use [`gemini/03_rate_limited_gemini.py`](gemini/03_rate_limited_gemini.py) to stay safely within free quotas.

2. **Groq LPU (Free Tier)**:
   - Sign up at [Groq Console](https://console.groq.com/).
   - Generous free tier with ultra-fast inference (~500 tokens/sec).
   - Explore [`groq/01_ultra_fast_swarm_groq.py`](groq/01_ultra_fast_swarm_groq.py).

3. **Ollama (100% Offline, Zero API Keys, Unlimited Free)**:
   - Install from [ollama.com](https://ollama.com).
   - Run `ollama run llama3:latest` or `ollama run gemma3:4b`.
   - Explore [`ollama/01_local_offline_quickstart.py`](ollama/01_local_offline_quickstart.py).

4. **Hugging Face Local GPU (Zero API Keys, Private)**:
   - Run open models on your CUDA GPU: `pip install 'swarmmy[hf]'`.
   - Explore [`huggingface/01_local_gpu_quickstart.py`](huggingface/01_local_gpu_quickstart.py).

---

## 🏃 Running the Examples

Each example script is fully standalone and can be executed directly:

```bash
# Gemini Examples
python examples/gemini/01_quickstart_gemini.py
python examples/gemini/02_code_review_gemini.py
python examples/gemini/03_rate_limited_gemini.py

# OpenAI Examples
python examples/openai/01_quickstart_openai.py
python examples/openai/02_system_design_openai.py
python examples/openai/03_budget_and_cost_cap_openai.py

# Anthropic Claude Examples
python examples/anthropic/01_quickstart_claude.py
python examples/anthropic/02_deep_reasoning_claude.py
python examples/anthropic/03_async_events_claude.py

# Groq Examples
python examples/groq/01_ultra_fast_swarm_groq.py
python examples/groq/02_creative_marketing_groq.py

# DeepSeek Examples
python examples/deepseek/01_deepseek_v3_swarm.py
python examples/deepseek/02_deepseek_r1_reasoning.py

# Local Ollama Examples
python examples/ollama/01_local_offline_quickstart.py
python examples/ollama/02_private_refactor_ollama.py

# Hugging Face Local GPU & Serverless Examples
python examples/huggingface/01_local_gpu_quickstart.py
python examples/huggingface/02_serverless_api_hf.py

# OpenRouter, Mistral, Cohere, Azure
python examples/openrouter/01_quickstart_openrouter.py
python examples/mistral/01_quickstart_mistral.py
python examples/cohere/01_quickstart_cohere.py
python examples/azure/01_quickstart_azure.py

# Custom Callables & FastAPI Streaming
python examples/custom_and_streaming/01_custom_callable_llm.py
python examples/custom_and_streaming/02_fastapi_sse_streaming.py
python examples/custom_and_streaming/03_event_hooks_and_tracing.py
```
