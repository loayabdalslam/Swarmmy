# ☁️ Azure OpenAI Provider Guide & Examples

Azure OpenAI allows enterprises to deploy OpenAI models inside their private Azure subscription, backed by enterprise SLA, virtual networks, and data privacy guarantees.

---

## 🔑 How to Set Up Your Azure OpenAI Configuration

### Required Parameters
To connect to Azure OpenAI, you need:
1. **API Key**: Found in Azure Portal under *Azure OpenAI Resource -> Keys and Endpoint*.
2. **Resource Name** (or Endpoint): E.g., `https://<my-resource>.openai.azure.com/`.
3. **Deployment Name**: The custom name you gave your deployed model in Azure AI Foundry / Studio.
4. **API Version**: (Defaults to `2024-08-01-preview` or your specified version).

---

### Environment Variables
- **PowerShell**:
  ```powershell
  $env:AZURE_OPENAI_API_KEY="YourAzureKey..."
  $env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
  ```
- **Bash**:
  ```bash
  export AZURE_OPENAI_API_KEY="YourAzureKey..."
  export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
  ```

---

## 📁 Examples in this Directory

- **[`01_quickstart_azure.py`](01_quickstart_azure.py)**: Running enterprise swarms on private Azure OpenAI deployments.
