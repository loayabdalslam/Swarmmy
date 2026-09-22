# 🐋 DeepSeek Provider Guide & Examples

DeepSeek provides frontier-grade open-architecture intelligence at a fraction of traditional API costs, including **DeepSeek-V3** (general multi-agent intelligence) and **DeepSeek-R1** (deep step-by-step reasoning).

---

## 🔑 How to Get and Set Up Your DeepSeek API Key

### 1. Obtain an API Key
1. Go to the **[DeepSeek Open Platform](https://platform.deepseek.com/)**.
2. Sign in and go to **API Keys**.
3. Generate a new API key (`sk-...`).

---

### 2. How to Set Your API Key

#### Option A: Environment Variable (Recommended)
Swarmmy automatically reads `DEEPSEEK_API_KEY`.

- **Windows PowerShell**:
  ```powershell
  $env:DEEPSEEK_API_KEY="sk-YourKeyHere..."
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set DEEPSEEK_API_KEY=sk-YourKeyHere...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export DEEPSEEK_API_KEY="sk-YourKeyHere..."
  ```

#### Option B: In a `.env` File
```env
DEEPSEEK_API_KEY=sk-YourKeyHere...
```

#### Option C: Directly in Python Code
```python
from swarmmy import create_provider

backend = create_provider("deepseek", model="deepseek-chat", api_key="sk-...")
```

#### Option D: Via Swarmmy CLI
```bash
swarmmy "Your prompt" --provider deepseek --live
```

---

## ⚙️ Recommended DeepSeek Models

| Model Name | Type | Best Used For |
| :--- | :--- | :--- |
| `deepseek-chat` | **Default** (DeepSeek-V3) | Ultra-fast general intelligence, code review, balanced critique |
| `deepseek-reasoner` | DeepSeek-R1 | Mathematical proofing, complex algorithm synthesis, deep chain-of-thought |

---

## 📁 Examples in this Directory

1. **[`01_deepseek_v3_swarm.py`](01_deepseek_v3_swarm.py)**: Running standard swarms with `deepseek-chat` (DeepSeek-V3).
2. **[`02_deepseek_r1_reasoning.py`](02_deepseek_r1_reasoning.py)**: Complex algorithmic reasoning with `deepseek-reasoner` (R1).
