# ⚡ Groq LPU Provider Guide & Examples

Groq provides unprecedented inference speed (often 500–800 tokens/second) powered by custom LPU (Language Processing Unit) silicon. This enables complete multi-agent swarms with 4 agents and multiple review rounds to finish in **under 2 to 3 seconds** total!

Groq also provides a generous **free tier**.

---

## 🔑 How to Get and Set Up Your Groq API Key

### 1. Obtain a Free API Key
1. Go to the **[Groq Console](https://console.groq.com/)**.
2. Sign in with GitHub or Google.
3. Navigate to **API Keys** and click **Create API Key**.

---

### 2. How to Set Your API Key

#### Option A: Environment Variable (Recommended)
Swarmmy automatically reads `GROQ_API_KEY`.

- **Windows PowerShell**:
  ```powershell
  $env:GROQ_API_KEY="gsk_YourKeyHere..."
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set GROQ_API_KEY=gsk_YourKeyHere...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export GROQ_API_KEY="gsk_YourKeyHere..."
  ```

#### Option B: In a `.env` File
```env
GROQ_API_KEY=gsk_YourKeyHere...
```

#### Option C: Directly in Python Code
```python
from swarmmy import create_provider

backend = create_provider("groq", model="llama-3.3-70b-versatile", api_key="gsk_...")
```

#### Option D: Via Swarmmy CLI
```bash
swarmmy "Your prompt" --provider groq --live
```

---

## ⚙️ Recommended Groq Models

| Model Name | Speed | Best Used For |
| :--- | :--- | :--- |
| `llama-3.3-70b-versatile` | **Default** (~300 t/s) | Flagship reasoning, coding, system design |
| `llama-3.1-8b-instant` | Blazing (~800 t/s) | Instant swarms, real-time UI/chat workflows |
| `mixtral-8x7b-32768` | Fast (~500 t/s) | Diverse perspectives, balanced reasoning |

---

## 📁 Examples in this Directory

1. **[`01_ultra_fast_swarm_groq.py`](01_ultra_fast_swarm_groq.py)**: Running a 4-agent swarm in ~1-2 seconds with real-time colored live display.
2. **[`02_creative_marketing_groq.py`](02_creative_marketing_groq.py)**: Rapid creative campaign brainstorming using `roles="creative"`.
