"""Showcase of all supported LLM providers in Swarmmy."""

from swarmmy import (
    AnthropicProvider,
    AzureOpenAIProvider,
    CohereProvider,
    Config,
    DeepSeekProvider,
    GeminiProvider,
    GroqProvider,
    HuggingFaceInferenceAPI,
    MistralProvider,
    OllamaProvider,
    OpenAIProvider,
    OpenRouterProvider,
    Swarm,
    create_provider,
)

# ==============================================================================
# 1. Google Gemini
# ==============================================================================
# Reads GEMINI_API_KEY or GOOGLE_API_KEY from environment
gemini_backend = create_provider("gemini", model="gemini-2.0-flash")
# Or directly:
# gemini_backend = GeminiProvider(model="gemini-2.0-flash", api_key="...")

# ==============================================================================
# 2. Anthropic Claude
# ==============================================================================
# Reads ANTHROPIC_API_KEY from environment
claude_backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022")

# ==============================================================================
# 3. OpenAI
# ==============================================================================
# Reads OPENAI_API_KEY from environment
openai_backend = create_provider("openai", model="gpt-4o-mini")

# ==============================================================================
# 4. Groq (Ultra-fast Llama 3.3 / Mixtral)
# ==============================================================================
# Reads GROQ_API_KEY from environment
groq_backend = create_provider("groq", model="llama-3.3-70b-versatile")

# ==============================================================================
# 5. DeepSeek
# ==============================================================================
# Reads DEEPSEEK_API_KEY from environment
deepseek_backend = create_provider("deepseek", model="deepseek-chat")

# ==============================================================================
# 6. Ollama (Local)
# ==============================================================================
# Connects to http://localhost:11434/v1
ollama_backend = create_provider("ollama", model="llama3:latest")

# ==============================================================================
# 7. Mistral AI
# ==============================================================================
# Reads MISTRAL_API_KEY from environment
mistral_backend = create_provider("mistral", model="mistral-large-latest")

# ==============================================================================
# 8. Cohere
# ==============================================================================
# Reads COHERE_API_KEY from environment
cohere_backend = create_provider("cohere", model="command-r-plus-08-2024")

# ==============================================================================
# 9. OpenRouter (Access 200+ models)
# ==============================================================================
# Reads OPENROUTER_API_KEY from environment
openrouter_backend = create_provider("openrouter", model="meta-llama/llama-3.3-70b-instruct")

# ==============================================================================
# 10. Azure OpenAI
# ==============================================================================
# azure_backend = create_provider(
#     "azure",
#     model="my-gpt4-deployment",
#     resource_name="my-azure-resource",
#     api_key="...",
# )

print("All provider definitions validated successfully!")
