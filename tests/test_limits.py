"""Unit tests for rate limits, token tracking, cost budgeting, and 429 retries."""

import asyncio
import json
import unittest

from swarmmy import (
    AsyncRateLimiter,
    Config,
    RateLimitExceededError,
    Result,
    Swarm,
    UsageLimitExceededError,
    UsageLimits,
    UsageReport,
    UsageTracker,
)


class FakeMockBackend:
    """Mock backend that tracks invocations and can simulate 429 rate limits."""

    def __init__(self, fail_429_times: int = 0):
        self.calls = 0
        self.fail_429_times = fail_429_times

    async def complete(self, messages, temperature=0.7, max_tokens=1024):
        self.calls += 1
        if self.fail_429_times > 0:
            self.fail_429_times -= 1
            raise ConnectionError("HTTP 429 Too Many Requests: Rate limit exceeded")

        p = messages[0]["content"]
        if p.startswith("Evaluate"):
            return json.dumps([{"id": 1, "score": 0.9, "critique": "Solid rationale."}])
        return "Standard mock solution."


class TestLimits(unittest.IsolatedAsyncioTestCase):
    """Test suite for rate limiting, token budgeting, and retry handling."""

    async def test_rate_limiter_basic(self):
        limiter = AsyncRateLimiter(rpm=60)
        # First call should have 0 wait
        waited = await limiter.acquire()
        self.assertEqual(waited, 0.0)

    async def test_rate_limiter_throttling(self):
        # 2 requests per minute limit
        limiter = AsyncRateLimiter(rpm=2)
        limiter.interval = 0.05  # Shortened interval for fast test
        w1 = await limiter.acquire()
        w2 = await limiter.acquire()
        self.assertEqual(w1, 0.0)
        self.assertEqual(w2, 0.0)

        # 3rd request must wait
        start = asyncio.get_event_loop().time()
        w3 = await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        self.assertGreater(w3, 0.0)
        self.assertGreaterEqual(elapsed, 0.04)

    def test_usage_limits_validation(self):
        with self.assertRaises(ValueError):
            UsageLimits(rpm=0)
        with self.assertRaises(ValueError):
            UsageLimits(max_total_tokens=-5)
        with self.assertRaises(ValueError):
            UsageLimits(max_cost_usd=-1.0)
        with self.assertRaises(ValueError):
            UsageLimits(max_retries=-1)

    async def test_usage_tracker_budget_exceeded(self):
        tracker = UsageTracker(UsageLimits(max_total_tokens=100))
        # Recording 80 tokens is fine
        await tracker.record_usage(
            prompt_text="short",
            completion_text="short",
            p_tokens=40,
            c_tokens=40,
        )
        self.assertEqual(tracker.total_tokens, 80)

        # Adding 50 tokens breaches 100 max_total_tokens
        with self.assertRaises(UsageLimitExceededError):
            await tracker.record_usage(
                prompt_text="overflow",
                completion_text="overflow",
                p_tokens=25,
                c_tokens=25,
            )

    async def test_cost_budget_exceeded(self):
        # Limit of $0.0001 USD
        tracker = UsageTracker(UsageLimits(max_cost_usd=0.0001))
        # High token usage should breach cost
        with self.assertRaises(UsageLimitExceededError):
            await tracker.record_usage(
                prompt_text="high usage",
                completion_text="high usage",
                model_name="gpt-4o",
                p_tokens=5000,
                c_tokens=5000,
            )

    async def test_swarm_token_limit_enforced(self):
        backend = FakeMockBackend()
        # Set tight token budget that will be breached
        config = Config(agents=2, rounds=0, max_total_tokens=10)
        with self.assertRaises(UsageLimitExceededError):
            await Swarm(backend, config).run("Test budget cap")

    async def test_retry_on_429_rate_limit(self):
        # Backend fails twice with 429, then succeeds
        backend = FakeMockBackend(fail_429_times=2)
        limits = UsageLimits(max_retries=3, min_retry_wait=0.01, retry_backoff_factor=1.5)
        config = Config(agents=2, rounds=0, limits=limits)

        result = await Swarm(backend, config).run("Test retry")
        self.assertIsInstance(result, Result)
        self.assertEqual(result.usage.retries_attempted, 2)
        self.assertTrue(result.answer)
        self.assertTrue(any("429" in w for w in result.warnings))

    async def test_result_contains_usage_report(self):
        backend = FakeMockBackend()
        config = Config(agents=2, rounds=0)
        result = await Swarm(backend, config).run("Simple run")

        self.assertIsInstance(result.usage, UsageReport)
        self.assertGreater(result.usage.total_tokens, 0)
        self.assertGreater(result.usage.prompt_tokens, 0)
        self.assertGreater(result.usage.completion_tokens, 0)
        self.assertGreaterEqual(result.usage.estimated_cost_usd, 0.0)

        # Check serialization in to_dict()
        as_dict = result.to_dict()
        self.assertIn("usage", as_dict)
        self.assertEqual(as_dict["usage"]["total_tokens"], result.usage.total_tokens)


if __name__ == "__main__":
    unittest.main()
