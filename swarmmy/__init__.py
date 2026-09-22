"""Swarmmy: Bounded peer-review swarm orchestration for instruction models."""

from .core import Config, Result, Swarm, run, run_sync
from .exceptions import (
    BudgetExhaustedError,
    ConfigurationError,
    ModelResponseError,
    ProviderError,
    RateLimitExceededError,
    ReviewParsingError,
    SwarmmyError,
    SynthesisError,
    UsageLimitExceededError,
)
from .limits import (
    MODEL_PRICING,
    PROVIDER_DEFAULT_LIMITS,
    AsyncRateLimiter,
    UsageLimits,
    UsageReport,
    UsageTracker,
    get_default_limits_for_provider,
)
from .providers import (
    PROVIDER_REGISTRY,
    AnthropicProvider,
    AzureOpenAIProvider,
    BaseProvider,
    CallableProvider,
    CohereProvider,
    DeepSeekProvider,
    GeminiProvider,
    GroqProvider,
    HuggingFace,
    HuggingFaceInferenceAPI,
    MistralProvider,
    OllamaProvider,
    OpenAICompatible,
    OpenAIProvider,
    OpenRouterProvider,
    create_provider,
)
from .printer import Colors, LivePrinter
from .roles import CODE_REVIEW_ROLES, CREATIVE_ROLES, DEFAULT_ROLES, resolve_roles
from .tunnel import (
    BaseTunnel,
    FunctionTunnel,
    StepEvent,
    StreamTunnel,
    WebSocketTunnel,
    WebhookTunnel,
)
from .types import Candidate, Review, TraceEvent

__version__ = "0.1.0"

__all__ = [
    # Core
    "Swarm",
    "Config",
    "Result",
    "run",
    "run_sync",
    # Types
    "Candidate",
    "Review",
    "TraceEvent",
    # Tunnels & Streaming
    "StepEvent",
    "BaseTunnel",
    "StreamTunnel",
    "WebhookTunnel",
    "WebSocketTunnel",
    "FunctionTunnel",
    # Display & Printer
    "LivePrinter",
    "Colors",
    # Providers & Factory
    "BaseProvider",
    "OpenAICompatible",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "GroqProvider",
    "DeepSeekProvider",
    "OllamaProvider",
    "MistralProvider",
    "CohereProvider",
    "OpenRouterProvider",
    "AzureOpenAIProvider",
    "HuggingFace",
    "HuggingFaceInferenceAPI",
    "CallableProvider",
    "create_provider",
    "PROVIDER_REGISTRY",
    # Limits & Usage
    "UsageLimits",
    "UsageReport",
    "UsageTracker",
    "AsyncRateLimiter",
    "MODEL_PRICING",
    "PROVIDER_DEFAULT_LIMITS",
    "get_default_limits_for_provider",
    # Roles
    "DEFAULT_ROLES",
    "CODE_REVIEW_ROLES",
    "CREATIVE_ROLES",
    "resolve_roles",
    # Exceptions
    "SwarmmyError",
    "ConfigurationError",
    "BudgetExhaustedError",
    "ProviderError",
    "ModelResponseError",
    "ReviewParsingError",
    "SynthesisError",
    "UsageLimitExceededError",
    "RateLimitExceededError",
]
