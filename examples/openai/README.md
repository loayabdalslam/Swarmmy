# 🟢 OpenAI Provider Guide & Examples

Swarmmy provides native, direct integration with OpenAI's models (GPT-4o, GPT-4o-mini, o1, o3-mini) using pure Python standard library with zero external SDK requirements.

---

## 🔑 How to Get and Set Up Your OpenAI API Key

### 1. Obtain an API Key
1. Go to the **[OpenAI API Platform](https://platform.openai.com/api-keys)**.
2. Sign in or create an account.
3. Generate a new secret key (starts with `sk-...` or `sk-proj-...`).

---

### 2. How to Set Your API Key

#### Option A: Environment Variable (Recommended)
Swarmmy automatically reads `OPENAI_API_KEY`.

- **Windows PowerShell**:
  ```powershell
  $env:OPENAI_API_KEY="sk-proj-YourKeyHere..."
  ```
  To set permanently:
  ```powershell
  [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-YourKeyHere...', 'User')
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set OPENAI_API_KEY=sk-proj-YourKeyHere...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export OPENAI_API_KEY="sk-proj-YourKeyHere..."
  ```

#### Option B: In a `.env` File
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=sk-proj-YourKeyHere...
```

#### Option C: Directly in Python Code
```python
from swarmmy import create_provider

backend = create_provider("openai", model="gpt-4o-mini", api_key="sk-proj-...")
```

#### Option D: Via Swarmmy CLI
```bash
swarmmy "Your task" --provider openai --model gpt-4o-mini --api-key "sk-..." --live
```

---

## ⚙️ Recommended OpenAI Models

| Model Name | Cost (per 1M input / output) | Best Used For |
| :--- | :--- | :--- |
| `gpt-4o-mini` | **Default** ($0.15 / $0.60) | Extremely cost-effective, high speed, perfect for multi-agent swarms |
| `gpt-4o` | Frontier ($2.50 / $10.00) | Complex reasoning, high-stakes architecture, detailed synthesis |
| `o3-mini` | Reasoning model | Complex STEM, competitive programming, logical verification |

---

## 📁 Examples in this Directory

1. **[`01_quickstart_openai.py`](01_quickstart_openai.py)**: Basic quickstart with `gpt-4o-mini` running both sync and async.
2. **[`02_system_design_openai.py`](02_system_design_openai.py)**: Distributed systems engineering deliberation with 4 specialized roles.
3. **[`03_budget_and_cost_cap_openai.py`](03_budget_and_cost_cap_openai.py)**: Setting hard USD financial cost ceilings and token limits to strictly cap API costs.
