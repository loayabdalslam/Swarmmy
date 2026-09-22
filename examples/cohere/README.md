# 🔷 Cohere Provider Guide & Examples

Cohere models (`command-r-plus-08-2024`, `command-r-08-2024`) are purpose-built for enterprise tasks, document synthesis, and multilingual applications.

---

## 🔑 How to Get and Set Up Your Cohere API Key

### 1. Obtain an API Key
1. Go to the **[Cohere Dashboard](https://dashboard.cohere.com/)**.
2. Sign in and generate a Trial or Production API key.

---

### 2. How to Set Your API Key

- **PowerShell**: `$env:COHERE_API_KEY="YourKeyHere..."`
- **Bash**: `export COHERE_API_KEY="YourKeyHere..."`
- **.env**: `COHERE_API_KEY=YourKeyHere...`

---

## 📁 Examples in this Directory

- **[`01_quickstart_cohere.py`](01_quickstart_cohere.py)**: Running enterprise swarms with Command R+.
