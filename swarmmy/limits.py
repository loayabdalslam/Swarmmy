"""Usage limits, rate limiting (RPM), and cost budgeting for Swarmmy."""

from __future__ import annotations

import asyncio
import collections
import dataclasses
import math
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from .exceptions import RateLimitExceededError, UsageLimitExceededError

# Approximate model pricing per 1,000,000 tokens (USD)
# Format: (input_price_per_1M, output_price_per_1M)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "o1": (15.00, 60.00),
    "o3-mini": (1.10, 4.40),
    # Anthropic
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-5-haiku": (0.80, 4.00),
    "claude-3-opus": (15.00, 75.00),
    # Google Gemini
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
    # DeepSeek
    "deepseek-chat": (0.14, 0.28),
    "deepseek-reasoner": (0.55, 2.19),
    # Groq / Open source hosted
    "llama-3.3-70b": (0.59, 0.79),
    "llama-3.1-8b": (0.05, 0.08),
    # Local models (Ollama, local HuggingFace)
    "ollama": (0.00, 0.00),
    "local": (0.00, 0.00),
    "qwen": (0.00, 0.00),
    "smollm": (0.00, 0.00),
    "hf": (0.00, 0.00),
}


def estimate_tokens(text: str) -> int:
    """Rough heuristic token estimator (~4 chars per token for Latin, ~2 for Arabic/CJK)."""
    if not text:
        return 0
    # Count Arabic/non-Latin characters separately
    arabic_or_cjk = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\u4E00-\u9FFF]", text))
    other_chars = len(text) - arabic_or_cjk
    tokens = (other_chars // 4) + (arabic_or_cjk // 2)
    return max(1, tokens)


def lookup_model_pricing(model_name: Any) -> tuple[float, float]:
    """Find the best matching pricing entry for a model name."""
    if not isinstance(model_name, str):
        if hasattr(model_name, "config") and hasattr(model_name.config, "_name_or_path"):
            model_name = str(model_name.config._name_or_path)
        else:
            model_name = str(model_name or "")
    name_lower = model_name.lower()
    for pattern, pricing in MODEL_PRICING.items():
        if pattern in name_lower:
            return pricing
    # Default fallback: $0.30 / $1.00 per million
    return (0.30, 1.00)


@dataclass
class UsageLimits:
    """Configuration for API rate limits and financial/token budgets.

    Attributes:
        rpm: Maximum requests per minute (throttling). If None, no RPM limit.
        tpm: Maximum tokens per minute (optional throttling).
        max_total_tokens: Hard ceiling on accumulated tokens across all calls.
        max_cost_usd: Hard ceiling on estimated spend in USD.
        max_retries: Number of retries when receiving HTTP 429 Too Many Requests.
        retry_backoff_factor: Multiplier for exponential backoff on rate limits.
        min_retry_wait: Minimum wait time in seconds before retrying a 429 error.
        max_retry_wait: Maximum wait time cap in seconds for retries.
    """
    rpm: int | None = None
    tpm: int | None = None
    max_total_tokens: int | None = None
    max_cost_usd: float | None = None
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    min_retry_wait: float = 1.0
    max_retry_wait: float = 60.0

    def __post_init__(self):
        if self.rpm is not None and self.rpm < 1:
            raise ValueError("rpm must be >= 1")
        if self.max_total_tokens is not None and self.max_total_tokens < 1:
            raise ValueError("max_total_tokens must be >= 1")
        if self.max_cost_usd is not None and self.max_cost_usd <= 0:
            raise ValueError("max_cost_usd must be > 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")


@dataclass
class UsageReport:
    """Summary of token consumption, financial cost, and rate-limiting metrics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    rate_limit_waits_seconds: float = 0.0
    calls_completed: int = 0
    retries_attempted: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AsyncRateLimiter:
    """Sliding-window asynchronous rate limiter for enforcing RPM limits."""

    def __init__(self, rpm: int | None):
        self.rpm = rpm
        self.interval = 60.0  # 60 seconds
        self._timestamps: collections.deque[float] = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> float:
        """Wait until a request slot is available under the RPM limit.

        Returns:
            The number of seconds waited (0.0 if immediately available).
        """
        if self.rpm is None or self.rpm <= 0:
            return 0.0

        async with self._lock:
            total_waited = 0.0
            while True:
                now = time.monotonic()
                # Purge timestamps older than 60 seconds
                while self._timestamps and now - self._timestamps[0] >= self.interval:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.rpm:
                    self._timestamps.append(now)
                    return total_waited

                # Need to wait until the oldest request expires
                oldest = self._timestamps[0]
                wait_time = max(0.01, self.interval - (now - oldest) + 0.05)
                total_waited += wait_time
                await asyncio.sleep(wait_time)


class UsageTracker:
    """Thread-safe and async-safe tracker for token usage, cost, and budget limits."""

    def __init__(self, limits: UsageLimits | None = None):
        self.limits = limits or UsageLimits()
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.estimated_cost_usd = 0.0
        self.rate_limit_waits_seconds = 0.0
        self.calls_completed = 0
        self.retries_attempted = 0
        self._lock = asyncio.Lock()

    async def record_usage(
        self,
        prompt_text: str,
        completion_text: str,
        model_name: str = "",
        p_tokens: int | None = None,
        c_tokens: int | None = None,
    ) -> None:
        """Record token consumption and check against budget limits."""
        async with self._lock:
            prompt_count = p_tokens if p_tokens is not None else estimate_tokens(prompt_text)
            comp_count = c_tokens if c_tokens is not None else estimate_tokens(completion_text)
            total = prompt_count + comp_count

            self.prompt_tokens += prompt_count
            self.completion_tokens += comp_count
            self.total_tokens += total
            self.calls_completed += 1

            # Estimate cost
            in_rate, out_rate = lookup_model_pricing(model_name)
            cost_inc = (prompt_count / 1_000_000 * in_rate) + (comp_count / 1_000_000 * out_rate)
            self.estimated_cost_usd += cost_inc

            # Check limits
            if self.limits.max_total_tokens and self.total_tokens > self.limits.max_total_tokens:
                raise UsageLimitExceededError(
                    f"Total token budget exceeded: {self.total_tokens} > {self.limits.max_total_tokens} tokens"
                )
            if self.limits.max_cost_usd and self.estimated_cost_usd > self.limits.max_cost_usd:
                raise UsageLimitExceededError(
                    f"Financial cost budget exceeded: ${self.estimated_cost_usd:.4f} > ${self.limits.max_cost_usd:.2f} USD"
                )

    async def record_wait(self, seconds: float) -> None:
        """Record time spent waiting due to rate limiting."""
        async with self._lock:
            self.rate_limit_waits_seconds += seconds

    async def record_retry(self) -> None:
        """Record a retry attempt on rate limit error."""
        async with self._lock:
            self.retries_attempted += 1

    def get_report(self) -> UsageReport:
        """Return a snapshot of current usage metrics."""
        return UsageReport(
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
            estimated_cost_usd=round(self.estimated_cost_usd, 6),
            rate_limit_waits_seconds=round(self.rate_limit_waits_seconds, 2),
            calls_completed=self.calls_completed,
            retries_attempted=self.retries_attempted,
        )


# Default safe limits per provider (protects free tiers and prevents crashes)
PROVIDER_DEFAULT_LIMITS: dict[str, UsageLimits] = {
    "gemini": UsageLimits(rpm=15, max_retries=3),       # Gemini Free Tier limit is 15 RPM
    "google": UsageLimits(rpm=15, max_retries=3),
    "groq": UsageLimits(rpm=30, max_retries=3),         # Groq Free Tier limit is 30 RPM
    "ollama": UsageLimits(rpm=None, max_retries=2),     # Local models
    "deepseek": UsageLimits(rpm=60, max_retries=3),
    "anthropic": UsageLimits(rpm=50, max_retries=3),
    "claude": UsageLimits(rpm=50, max_retries=3),
    "openai": UsageLimits(rpm=60, max_retries=3),
    "mistral": UsageLimits(rpm=60, max_retries=3),
    "cohere": UsageLimits(rpm=40, max_retries=3),
    "openrouter": UsageLimits(rpm=60, max_retries=3),
}


def get_default_limits_for_provider(provider_name: str | None) -> UsageLimits:
    """Return default safe usage limits for a given provider, or default UsageLimits."""
    if not provider_name:
        return UsageLimits()
    return PROVIDER_DEFAULT_LIMITS.get(provider_name.lower().strip(), UsageLimits())
