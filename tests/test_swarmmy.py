"""Comprehensive tests for Swarmmy library."""

import asyncio
import json
import unittest

from swarmmy import (
    BudgetExhaustedError,
    CallableProvider,
    Candidate,
    CODE_REVIEW_ROLES,
    Config,
    ConfigurationError,
    DEFAULT_ROLES,
    Result,
    Review,
    Swarm,
    TraceEvent,
    resolve_roles,
    run,
    run_sync,
)


class FakeBackend:
    """Mock backend for deterministic swarm testing."""

    def __init__(self, malformed=False, fail=False, slow=False):
        self.active = self.peak = 0
        self.malformed = malformed
        self.fail = fail
        self.slow = slow

    async def complete(self, messages, temperature=0.7, max_tokens=1024):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            if self.slow:
                await asyncio.sleep(0.005)
            else:
                await asyncio.sleep(0.001)

            p = messages[0]["content"]
            if self.fail:
                raise ConnectionError("Mock connection failure")
            if p.startswith("Evaluate"):
                if self.malformed:
                    return "not a valid json string"
                data = json.loads(p[p.index('{"task"'):])
                return json.dumps([
                    {"id": x["id"], "score": 0.85, "critique": "Solid rationale, consider edge cases."}
                    for x in data["material"]
                ])
            return "Synthetic swarm answer candidate."
        finally:
            self.active -= 1


class TestSwarmmy(unittest.IsolatedAsyncioTestCase):
    """Test suite for core Swarmmy behaviors."""

    async def test_standard_lifecycle_and_concurrency(self):
        backend = FakeBackend()
        config = Config(agents=4, rounds=1, concurrency=2)
        swarm = Swarm(backend, config)
        result = await swarm.run("Design a scalable cache system")

        self.assertIsInstance(result, Result)
        self.assertEqual(result.calls, 17)  # 4 * (2 + 2*1) + 1
        self.assertEqual(len(result.candidates), 4)
        self.assertEqual(len(result.reviews), 12)  # 4 * 3
        self.assertTrue(all(r.reviewer != r.id for r in result.reviews))
        self.assertEqual(backend.peak, 2)
        self.assertTrue(result.answer)
        self.assertIsInstance(result.candidates[0], Candidate)
        self.assertEqual(result.candidates[0].text, result.candidates[0]["text"])

    async def test_zero_rounds(self):
        backend = FakeBackend()
        config = Config(agents=4, rounds=0)
        result = await Swarm(backend, config).run("Fast lookup")
        self.assertEqual(result.calls, 9)  # 4 * (2 + 0) + 1

    async def test_events_hook(self):
        backend = FakeBackend()
        events_received = []

        def on_event(ev: TraceEvent):
            events_received.append(ev)

        swarm = Swarm(backend, Config(agents=2, rounds=0, concurrency=2), on_event=on_event)
        result = await swarm.run("Small task")

        self.assertEqual(len(events_received), result.calls)
        self.assertTrue(all(isinstance(e, TraceEvent) for e in events_received))
        self.assertEqual(events_received[0].stage, "propose")
        self.assertEqual(events_received[-1].stage, "synthesize")

    async def test_callable_provider_sync(self):
        def my_sync_fn(messages, temperature=0.7, max_tokens=1024):
            p = messages[0]["content"]
            if p.startswith("Evaluate"):
                data = json.loads(p[p.index('{"task"'):])
                return json.dumps([{"id": x["id"], "score": 0.9, "critique": "Good"} for x in data["material"]])
            return "From sync callable"

        provider = CallableProvider(my_sync_fn)
        result = await Swarm(provider, Config(agents=2, rounds=0)).run("Test callable")
        self.assertEqual(result.answer, "From sync callable")

    async def test_callable_passed_directly_to_swarm(self):
        async def my_async_fn(messages, temperature=0.7, max_tokens=1024):
            p = messages[0]["content"]
            if p.startswith("Evaluate"):
                data = json.loads(p[p.index('{"task"'):])
                return json.dumps([{"id": x["id"], "score": 0.9, "critique": "Good"} for x in data["material"]])
            return "Direct callable output"

        # Swarm should auto-wrap callable in CallableProvider
        swarm = Swarm(my_async_fn, Config(agents=2, rounds=0))
        result = await swarm.run("Direct test")
        self.assertEqual(result.answer, "Direct callable output")

    def test_run_sync(self):
        backend = FakeBackend()
        result = run_sync("Synchronous task", backend, Config(agents=2, rounds=0))
        self.assertIsInstance(result, Result)
        self.assertEqual(result.calls, 5)

    async def test_roles_presets(self):
        roles_default = resolve_roles()
        self.assertEqual(roles_default, DEFAULT_ROLES)

        roles_code = resolve_roles("code")
        self.assertEqual(roles_code, CODE_REVIEW_ROLES)

        custom = resolve_roles(["Role 1", "Role 2"])
        self.assertEqual(custom, ("Role 1", "Role 2"))

        with self.assertRaises(ValueError):
            resolve_roles("nonexistent_preset")

    async def test_malformed_reviews_recovery(self):
        backend = FakeBackend(malformed=True)
        result = await Swarm(backend, Config(agents=3, rounds=1)).run("Handle bad json")
        self.assertEqual(result.reviews, [])
        self.assertTrue(result.warnings)
        self.assertTrue(all(c.peer_score is None for c in result.candidates))

    async def test_total_failure_raises(self):
        backend = FakeBackend(fail=True)
        with self.assertRaises(RuntimeError):
            await Swarm(backend, Config()).run("Must fail")

    async def test_budget_exceeded(self):
        backend = FakeBackend()
        # Setting max_calls manually below required raises ConfigurationError
        with self.assertRaises(ConfigurationError):
            Config(agents=4, rounds=1, max_calls=10)

    async def test_empty_task_raises(self):
        with self.assertRaises(ConfigurationError):
            await Swarm(FakeBackend()).run("   ")

    async def test_result_serialization(self):
        backend = FakeBackend()
        result = await Swarm(backend, Config(agents=2, rounds=0)).run("Serialization test")
        as_dict = result.to_dict()
        self.assertIn("answer", as_dict)
        self.assertIn("candidates", as_dict)
        self.assertIn("trace", as_dict)
        json_str = result.to_json()
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["answer"], result.answer)


if __name__ == "__main__":
    unittest.main()
