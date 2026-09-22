# 🟣 Anthropic Claude Provider Guide & Examples

Anthropic Claude models (`claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`, `claude-3-opus-20240229`) are renowned for state-of-the-art coding, critical nuance, and intellectual honesty during peer review.

---

## 🔑 How to Get and Set Up Your Anthropic API Key

### 1. Obtain an API Key
1. Go to the **[Anthropic Console](https://console.anthropic.com/)**.
2. Sign in and navigate to **API Keys**.
3. Create a key (starts with `sk-ant-api03-...`).

---

### 2. How to Set Your API Key

#### Option A: Environment Variable (Recommended)
Swarmmy automatically reads `ANTHROPIC_API_KEY`.

- **Windows PowerShell**:
  ```powershell
  $env:ANTHROPIC_API_KEY="sk-ant-api03-YourKeyHere..."
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set ANTHROPIC_API_KEY=sk-ant-api03-YourKeyHere...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-api03-YourKeyHere..."
  ```

#### Option B: In a `.env` File
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=sk-ant-api03-YourKeyHere...
```

#### Option C: Directly in Python Code
```python
from swarmmy import create_provider

backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022", api_key="sk-ant-...")
```

#### Option D: Via Swarmmy CLI
```bash
swarmmy "Your task" --provider anthropic --live
```

---

## ⚙️ Recommended Claude Models

| Model Name | Strengths | Best Used For |
| :--- | :--- | :--- |
| `claude-3-5-sonnet-20241022` | **Default**. Industry-leading code and reasoning. | High-stakes architecture, multi-round peer reviews |
| `claude-3-5-haiku-20241022` | Lightning-fast, economical. | Rapid brainstorming, lightweight peer reviews |
| `claude-3-opus-20240229` | Deepest analytical comprehension. | Complex policy evaluation, legal/medical review |

---

## 📁 Examples in this Directory

1. **[`01_quickstart_claude.py`](01_quickstart_claude.py)**: Standard swarm deliberation with Claude 3.5 Sonnet.
2. **[`02_deep_reasoning_claude.py`](02_deep_reasoning_claude.py)**: Multi-round (`rounds=2`) scientific / algorithmic peer evaluation.
3. **[`03_async_events_claude.py`](03_async_events_claude.py)**: Asynchronous swarm execution with lifecycle event tracking hooks.
