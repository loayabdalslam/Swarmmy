"""Unit tests for Swarmmy LLM providers and provider factory."""

import asyncio
import json
import os
import unittest
from unittest.mock import MagicMock, patch

from swarmmy.exceptions import ModelResponseError, ProviderError
from swarmmy.providers import (
    AnthropicProvider,
    AzureOpenAIProvider,
    CohereProvider,
    DeepSeekProvider,
    GeminiProvider,
    GroqProvider,
    HuggingFaceInferenceAPI,
    MistralProvider,
    OllamaProvider,
    OpenAICompatible,
    OpenAIProvider,
    OpenRouterProvider,
    create_provider,
)


class TestProviders(unittest.IsolatedAsyncioTestCase):
    """Test suite for provider instantiation, message serialization, and responses."""

    def test_create_provider_factory(self):
        self.assertIsInstance(create_provider("openai", "gpt-4o"), OpenAIProvider)
        self.assertIsInstance(create_provider("anthropic", "claude-3-5-sonnet-20241022"), AnthropicProvider)
        self.assertIsInstance(create_provider("claude", "claude-3-5-sonnet-20241022"), AnthropicProvider)
        self.assertIsInstance(create_provider("gemini", "gemini-2.0-flash"), GeminiProvider)
        self.assertIsInstance(create_provider("google", "gemini-2.0-flash"), GeminiProvider)
        self.assertIsInstance(create_provider("groq", "llama-3.3-70b-versatile"), GroqProvider)
        self.assertIsInstance(create_provider("deepseek", "deepseek-chat"), DeepSeekProvider)
        self.assertIsInstance(create_provider("ollama", "llama3:latest"), OllamaProvider)
        self.assertIsInstance(create_provider("mistral", "mistral-large-latest"), MistralProvider)
        self.assertIsInstance(create_provider("cohere", "command-r-plus"), CohereProvider)
        self.assertIsInstance(create_provider("openrouter", "meta-llama/llama-3"), OpenRouterProvider)
        self.assertIsInstance(create_provider("hf-api", "meta-llama/llama-3"), HuggingFaceInferenceAPI)
        self.assertIsInstance(create_provider("api", "custom-model"), OpenAICompatible)

        with self.assertRaises(ValueError):
            create_provider("invalid_provider_name")

    @patch("urllib.request.urlopen")
    async def test_openai_compatible_complete(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "OpenAI answer"}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = OpenAICompatible(model="test-model", api_key="secret-key")
        result = await provider.complete([{"role": "user", "content": "Hello"}])

        self.assertEqual(result, "OpenAI answer")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.headers["Authorization"], "Bearer secret-key")
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "test-model")

    @patch("urllib.request.urlopen")
    async def test_anthropic_provider_complete(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "content": [{"text": "Claude response"}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = AnthropicProvider(model="claude-3-5-sonnet", api_key="claude-key")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello Claude"},
        ]
        result = await provider.complete(messages, temperature=0.5, max_tokens=500)

        self.assertEqual(result, "Claude response")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.headers["X-api-key"], "claude-key")
        self.assertEqual(req.headers["Anthropic-version"], "2023-06-01")
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["system"], "You are a helpful assistant.")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Hello Claude"}])
        self.assertEqual(payload["max_tokens"], 500)

    @patch("urllib.request.urlopen")
    async def test_gemini_provider_complete(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {"parts": [{"text": "Gemini answer"}]}
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = GeminiProvider(model="gemini-2.0-flash", api_key="gemini-key")
        messages = [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hi Gemini"},
        ]
        result = await provider.complete(messages, temperature=0.8, max_tokens=600)

        self.assertEqual(result, "Gemini answer")
        req = mock_urlopen.call_args[0][0]
        self.assertIn("key=gemini-key", req.full_url)
        payload = json.loads(req.data.decode("utf-8"))
        self.assertIn("systemInstruction", payload)
        self.assertEqual(payload["contents"][0]["role"], "user")
        self.assertEqual(payload["contents"][0]["parts"][0]["text"], "Hi Gemini")

    @patch("urllib.request.urlopen")
    async def test_cohere_provider_complete(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "message": {"content": [{"text": "Cohere answer"}]}
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = CohereProvider(model="command-r-plus", api_key="cohere-key")
        result = await provider.complete([{"role": "user", "content": "Hello"}])

        self.assertEqual(result, "Cohere answer")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.headers["Authorization"], "Bearer cohere-key")
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "command-r-plus")

    @patch("urllib.request.urlopen")
    async def test_azure_openai_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Azure answer"}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = AzureOpenAIProvider(
            deployment="gpt-4o",
            resource_name="my-resource",
            api_key="azure-key",
        )
        result = await provider.complete([{"role": "user", "content": "Hello"}])

        self.assertEqual(result, "Azure answer")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.headers["Api-key"], "azure-key")
        self.assertIn("https://my-resource.openai.azure.com", req.full_url)

    @patch("urllib.request.urlopen")
    async def test_empty_response_raises_model_response_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "   "}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        provider = OpenAICompatible(model="test")
        with self.assertRaises(ModelResponseError):
            await provider.complete([{"role": "user", "content": "Hi"}])


if __name__ == "__main__":
    unittest.main()
