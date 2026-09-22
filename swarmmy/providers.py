"""Model inference backends for Swarmmy with first-class multi-provider support."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Sequence, Union

from .exceptions import ModelResponseError, ProviderError


class BaseProvider(ABC):
    """Abstract base class for all Swarmmy inference providers."""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a completion for the given chat messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature (0.0 to 1.0+).
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated response string.
        """
        raise NotImplementedError


def _send_http_request(
    url: str,
    payload_dict: dict[str, Any],
    headers: dict[str, str],
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Execute a synchronous JSON HTTP POST request via urllib."""
    data = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise ProviderError(f"HTTP {e.code} from {url}: {e.reason} {body[:200]}") from e
    except urllib.error.URLError as e:
        raise ProviderError(f"Network error connecting to {url}: {type(e).__name__}") from e
    except json.JSONDecodeError as e:
        raise ModelResponseError(f"Invalid JSON received from {url}: {e}") from e


class OpenAICompatible(BaseProvider):
    """Provider for any OpenAI-compatible API server (vLLM, Ollama, OpenAI, TGI, etc.)."""

    def __init__(
        self,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        timeout: float = 120.0,
        extra_headers: dict[str, str] | None = None,
    ):
        self.model = model
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.timeout = timeout
        self.extra_headers = extra_headers or {}

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        def _call() -> str:
            result = _send_http_request(self.url, payload, headers, timeout=self.timeout)
            try:
                content = result["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise ModelResponseError("Provider returned empty or non-text response content")
                return content
            except (KeyError, IndexError) as e:
                raise ModelResponseError(f"Unexpected response structure from OpenAICompatible: {e}") from e

        return await asyncio.to_thread(_call)


class OpenAIProvider(OpenAICompatible):
    """Convenience alias for OpenAI official API."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 120.0,
        **kwargs: Any,
    ):
        super().__init__(
            model=model,
            base_url=base_url,
            api_key=api_key or os.getenv("OPENAI_API_KEY", ""),
            timeout=timeout,
            **kwargs,
        )


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider via Messages API (zero extra dependencies)."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str = "",
        base_url: str = "https://api.anthropic.com/v1",
        timeout: float = 120.0,
    ):
        self.model = model
        self.url = base_url.rstrip("/") + "/messages"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.timeout = timeout

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        system_parts = []
        user_assistant_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                user_assistant_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"],
                })

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": user_assistant_messages,
            "max_tokens": max_tokens,
            "temperature": min(max(temperature, 0.0), 1.0),
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)

        def _call() -> str:
            result = _send_http_request(self.url, payload, headers, timeout=self.timeout)
            try:
                content = result["content"][0]["text"]
                if not isinstance(content, str) or not content.strip():
                    raise ModelResponseError("Anthropic returned empty response content")
                return content
            except (KeyError, IndexError) as e:
                raise ModelResponseError(f"Unexpected response structure from Anthropic: {e}") from e

        return await asyncio.to_thread(_call)


class GeminiProvider(BaseProvider):
    """Google Gemini provider via Google AI Studio REST API (zero extra dependencies)."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: str = "",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout: float = 120.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        self.timeout = timeout

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        contents = []
        system_instruction = None

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = {"parts": [{"text": msg["content"]}]}
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        def _call() -> str:
            result = _send_http_request(url, payload, headers, timeout=self.timeout)
            try:
                candidate = result["candidates"][0]
                text = candidate["content"]["parts"][0]["text"]
                if not isinstance(text, str) or not text.strip():
                    raise ModelResponseError("Gemini returned empty response text")
                return text
            except (KeyError, IndexError) as e:
                raise ModelResponseError(f"Unexpected response structure from Gemini: {e}") from e

        return await asyncio.to_thread(_call)


class GroqProvider(OpenAICompatible):
    """Groq ultra-fast Llama/Mixtral cloud inference provider."""

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        api_key: str = "",
        timeout: float = 60.0,
        **kwargs: Any,
    ):
        super().__init__(
            model=model,
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key or os.getenv("GROQ_API_KEY", ""),
            timeout=timeout,
            **kwargs,
        )


class DeepSeekProvider(OpenAICompatible):
    """DeepSeek official API provider (DeepSeek-V3, DeepSeek-R1)."""

    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: str = "",
        base_url: str = "https://api.deepseek.com",
        timeout: float = 120.0,
        **kwargs: Any,
    ):
        super().__init__(
            model=model,
            base_url=base_url,
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY", ""),
            timeout=timeout,
            **kwargs,
        )


class OllamaProvider(OpenAICompatible):
    """Local Ollama instance provider via Ollama OpenAI-compatible endpoint."""

    def __init__(
        self,
        model: str = "llama3:latest",
        base_url: str = "",
        timeout: float = 300.0,
        **kwargs: Any,
    ):
        host = base_url or os.getenv("OLLAMA_HOST") or "http://localhost:11434"
        if not host.endswith("/v1"):
            host = host.rstrip("/") + "/v1"
        super().__init__(
            model=model,
            base_url=host,
            api_key="ollama",
            timeout=timeout,
            **kwargs,
        )


class MistralProvider(OpenAICompatible):
    """Mistral AI official API provider (Mistral Large, Codestral)."""

    def __init__(
        self,
        model: str = "mistral-large-latest",
        api_key: str = "",
        timeout: float = 120.0,
        **kwargs: Any,
    ):
        super().__init__(
            model=model,
            base_url="https://api.mistral.ai/v1",
            api_key=api_key or os.getenv("MISTRAL_API_KEY", ""),
            timeout=timeout,
            **kwargs,
        )


class OpenRouterProvider(OpenAICompatible):
    """OpenRouter universal gateway provider supporting 200+ models."""

    def __init__(
        self,
        model: str,
        api_key: str = "",
        timeout: float = 120.0,
        app_name: str = "Swarmmy",
        app_url: str = "",
        **kwargs: Any,
    ):
        extra_headers = kwargs.pop("extra_headers", {})
        if app_url:
            extra_headers["HTTP-Referer"] = app_url
        if app_name:
            extra_headers["X-Title"] = app_name

        super().__init__(
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key or os.getenv("OPENROUTER_API_KEY", ""),
            timeout=timeout,
            extra_headers=extra_headers,
            **kwargs,
        )


class CohereProvider(BaseProvider):
    """Cohere provider using Cohere v2 Chat API."""

    def __init__(
        self,
        model: str = "command-r-plus-08-2024",
        api_key: str = "",
        base_url: str = "https://api.cohere.com/v2",
        timeout: float = 120.0,
    ):
        self.model = model
        self.url = base_url.rstrip("/") + "/chat"
        self.api_key = api_key or os.getenv("COHERE_API_KEY", "")
        self.timeout = timeout

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        cohere_messages = [
            {"role": msg["role"] if msg["role"] in ("user", "assistant", "system") else "user", "content": msg["content"]}
            for msg in messages
        ]
        payload = {
            "model": self.model,
            "messages": cohere_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        def _call() -> str:
            result = _send_http_request(self.url, payload, headers, timeout=self.timeout)
            try:
                content = result["message"]["content"][0]["text"]
                if not isinstance(content, str) or not content.strip():
                    raise ModelResponseError("Cohere returned empty response content")
                return content
            except (KeyError, IndexError) as e:
                raise ModelResponseError(f"Unexpected response structure from Cohere: {e}") from e

        return await asyncio.to_thread(_call)


class AzureOpenAIProvider(BaseProvider):
    """Microsoft Azure OpenAI Service provider."""

    def __init__(
        self,
        deployment: str,
        resource_name: str = "",
        api_key: str = "",
        api_version: str = "2024-06-01",
        base_url: str = "",
        timeout: float = 120.0,
    ):
        self.deployment = deployment
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
        self.timeout = timeout

        if base_url:
            self.url = f"{base_url.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
        else:
            resource = resource_name or os.getenv("AZURE_OPENAI_RESOURCE", "")
            if not resource:
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
                if endpoint:
                    self.url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
                else:
                    raise ValueError("Provide either resource_name, base_url, or AZURE_OPENAI_ENDPOINT")
            else:
                self.url = f"https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        def _call() -> str:
            result = _send_http_request(self.url, payload, headers, timeout=self.timeout)
            try:
                content = result["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise ModelResponseError("Azure OpenAI returned empty response content")
                return content
            except (KeyError, IndexError) as e:
                raise ModelResponseError(f"Unexpected response structure from Azure OpenAI: {e}") from e

        return await asyncio.to_thread(_call)


class HuggingFaceInferenceAPI(BaseProvider):
    """Hugging Face Serverless Inference API backend."""

    def __init__(
        self,
        model: str,
        api_key: str = "",
        timeout: float = 120.0,
    ):
        self.model = model
        self.url = f"https://api-inference.huggingface.co/models/{model}"
        self.api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY", "")
        self.timeout = timeout

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        # Format conversation prompt for general text-generation
        prompt = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages) + "\nAssistant: "
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": max(temperature, 0.01),
                "max_new_tokens": max_tokens,
                "return_full_text": False,
            },
        }

        def _call() -> str:
            result = _send_http_request(self.url, payload, headers, timeout=self.timeout)
            try:
                if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                    return result[0]["generated_text"].strip()
                raise ModelResponseError(f"Unexpected response from HF Inference API: {result}")
            except Exception as e:
                raise ModelResponseError(f"Failed to parse HF response: {e}") from e

        return await asyncio.to_thread(_call)


class HuggingFace(BaseProvider):
    """Local Hugging Face CausalLM backend with generation serialization to prevent VRAM spikes."""

    def __init__(
        self,
        model: str,
        device_map: str = "auto",
        context_tokens: int = 8192,
        trust_remote_code: bool = False,
    ):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "HuggingFace backend requires extra dependencies. Install with: pip install 'swarmmy[hf]'"
            ) from e

        import threading

        self.model_name = model
        self.tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=trust_remote_code)
        self.model = AutoModelForCausalLM.from_pretrained(
            model, device_map=device_map, trust_remote_code=trust_remote_code
        )
        self.model.eval()
        self.lock = threading.Lock()
        limit = getattr(self.model.config, "max_position_embeddings", context_tokens)
        self.context_tokens = min(context_tokens, limit)

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        def _generate() -> str:
            import torch

            with self.lock, torch.inference_mode():
                inputs = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=True,
                    add_generation_prompt=True,
                    return_tensors="pt",
                    return_dict=True,
                )
                input_len = inputs["input_ids"].shape[-1]
                if input_len + max_tokens > self.context_tokens:
                    raise ValueError(
                        f"Context limit exceeded ({input_len + max_tokens} > {self.context_tokens}). "
                        "Reduce peer_chars, max_tokens, or number of agents."
                    )
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
                kwargs: dict[str, Any] = {
                    "max_new_tokens": max_tokens,
                    "do_sample": temperature > 0,
                }
                if temperature > 0:
                    kwargs["temperature"] = temperature
                output = self.model.generate(**inputs, **kwargs)
                return self.tokenizer.decode(
                    output[0, input_len:], skip_special_tokens=True
                )

        return await asyncio.to_thread(_generate)


CallableFunction = Union[
    Callable[..., str],
    Callable[..., Coroutine[Any, Any, str]],
]


class CallableProvider(BaseProvider):
    """Adapter to wrap any custom Python function or coroutine as a Swarmmy provider."""

    def __init__(self, fn: CallableFunction):
        self._fn = fn
        self._is_async = inspect.iscoroutinefunction(fn)

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if self._is_async:
            result = await self._fn(messages, temperature=temperature, max_tokens=max_tokens)
        else:
            result = await asyncio.to_thread(
                self._fn, messages, temperature=temperature, max_tokens=max_tokens
            )
        if not isinstance(result, str) or not result.strip():
            raise ModelResponseError("CallableProvider function returned empty or non-string response")
        return result


PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,
    "gemini": GeminiProvider,
    "google": GeminiProvider,
    "groq": GroqProvider,
    "deepseek": DeepSeekProvider,
    "ollama": OllamaProvider,
    "mistral": MistralProvider,
    "cohere": CohereProvider,
    "openrouter": OpenRouterProvider,
    "azure": AzureOpenAIProvider,
    "azure-openai": AzureOpenAIProvider,
    "hf": HuggingFace,
    "huggingface": HuggingFace,
    "hf-api": HuggingFaceInferenceAPI,
    "api": OpenAICompatible,
    "openai-compatible": OpenAICompatible,
}


def create_provider(
    provider: str,
    model: str | None = None,
    api_key: str = "",
    base_url: str = "",
    **kwargs: Any,
) -> BaseProvider:
    """Factory function to instantiate any supported LLM provider by name.

    Args:
        provider: Provider identifier (e.g. 'openai', 'anthropic', 'gemini', 'groq',
                  'deepseek', 'ollama', 'mistral', 'cohere', 'openrouter', 'azure', 'hf').
        model: Target model name or identifier.
        api_key: Provider API key (optional; defaults to provider's environment variable).
        base_url: Custom API endpoint URL (optional).
        **kwargs: Additional provider-specific parameters.

    Returns:
        An instance of BaseProvider ready for Swarm execution.

    Example:
        ```python
        from swarmmy import create_provider, Swarm

        backend = create_provider("gemini", model="gemini-2.0-flash")
        backend = create_provider("anthropic", model="claude-3-5-sonnet-20241022")
        backend = create_provider("groq", model="llama-3.3-70b-versatile")
        backend = create_provider("ollama", model="llama3:latest")
        ```
    """
    key = provider.lower().strip()
    cls = PROVIDER_REGISTRY.get(key)
    if cls is None:
        valid_keys = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
        raise ValueError(f"Unknown provider '{provider}'. Supported providers: {valid_keys}")

    # Build constructor kwargs based on provider type
    init_kwargs: dict[str, Any] = dict(kwargs)
    if model is not None:
        if cls is AzureOpenAIProvider and "deployment" not in init_kwargs:
            init_kwargs["deployment"] = model
        else:
            init_kwargs["model"] = model

    if api_key:
        init_kwargs["api_key"] = api_key
    if base_url:
        init_kwargs["base_url"] = base_url

    return cls(**init_kwargs)
