# ♊ Google Gemini Provider Guide & Examples

Google Gemini offers high throughput, long context windows, and a generous **free tier** via Google AI Studio.

---

## 🔑 How to Get and Set Up Your Gemini API Key

### 1. Obtain a Free API Key
1. Go to **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your Google account.
3. Click **"Get API key"** and create a new key.

---

### 2. How to Set Your API Key

#### Option A: Environment Variable (Recommended)
Swarmmy automatically checks for `GEMINI_API_KEY` or `GOOGLE_API_KEY`.

- **Windows PowerShell**:
  ```powershell
  $env:GEMINI_API_KEY="AIzaSyYourActualKeyHere..."
  ```
  To set permanently on Windows:
  ```powershell
  [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSyYourActualKeyHere...', 'User')
  ```

- **Windows Command Prompt (CMD)**:
  ```cmd
  set GEMINI_API_KEY=AIzaSyYourActualKeyHere...
  ```

- **macOS / Linux (Bash or Zsh)**:
  ```bash
  export GEMINI_API_KEY="AIzaSyYourActualKeyHere..."
  ```
  Add it to your `~/.bashrc` or `~/.zshrc` to make it permanent.

#### Option B: In a `.env` File
Create a `.env` file in your project root:
```env
GEMINI_API_KEY=AIzaSyYourActualKeyHere...
```

#### Option C: Directly in Python Code
```python
from swarmmy import create_provider

backend = create_provider("gemini", api_key="AIzaSyYourActualKeyHere...")
```

#### Option D: Via Swarmmy CLI
```bash
swarmmy "Your task prompt" --provider gemini --api-key "AIzaSy..." --live
```

---

## ⚙️ Recommended Gemini Models

| Model Name | Description | Best Used For |
| :--- | :--- | :--- |
| `gemini-2.0-flash` | **Default**. Ultra-fast, highly intelligent, native multimodality. | General swarms, coding, rapid reasoning |
| `gemini-1.5-pro` | Maximum reasoning depth, 2M token context window. | Deep document analysis, multi-round audits |
| `gemini-1.5-flash` | Lightweight, economical, high RPM. | High-frequency swarms, quick tasks |

---

## 🛡️ Free Tier Rate Limiting Tip
Google AI Studio's free tier has a limit of **15 requests per minute (RPM)**. Swarmmy has built-in rate-limiting protection so you never trigger HTTP 429:

```python
from swarmmy import Config, UsageLimits

# Automatically spaces calls to stay under 15 RPM
limits = UsageLimits(rpm=15, max_retries=3)
config = Config(agents=3, rounds=1, limits=limits)
```

---

## 📁 Examples in this Directory

1. **[`01_quickstart_gemini.py`](01_quickstart_gemini.py)**: Basic synchronous and asynchronous swarm execution using `gemini-2.0-flash`.
2. **[`02_code_review_gemini.py`](02_code_review_gemini.py)**: Specialized security code audit using peer review with custom AppSec personas.
3. **[`03_rate_limited_gemini.py`](03_rate_limited_gemini.py)**: Running swarms safely within free-tier 15 RPM quotas with token & budget tracking.
