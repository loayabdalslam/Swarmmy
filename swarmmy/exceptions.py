"""Custom exceptions for the Swarmmy library."""


class SwarmmyError(Exception):
    """Base exception for all errors raised by Swarmmy."""


class ConfigurationError(SwarmmyError, ValueError):
    """Raised when configuration parameters are invalid."""


class BudgetExhaustedError(SwarmmyError, RuntimeError):
    """Raised when the maximum allowed API calls budget is exhausted."""


class ProviderError(SwarmmyError):
    """Raised when an inference provider fails to complete a request."""


class ModelResponseError(ProviderError, ValueError):
    """Raised when a model response is empty, malformed, or of invalid type."""


class ReviewParsingError(SwarmmyError):
    """Raised when peer review responses cannot be validated or parsed."""


class SynthesisError(SwarmmyError):
    """Raised when synthesis stage fails to produce an aggregated answer."""


class UsageLimitExceededError(SwarmmyError):
    """Raised when a token or financial cost limit is exceeded."""


class RateLimitExceededError(ProviderError):
    """Raised when an HTTP 429 Too Many Requests persists after all retry attempts."""
