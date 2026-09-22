"""Unit tests for the real-time API Tunnel system and event streaming in Swarmmy."""

import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch

from swarmmy import (
    BaseTunnel,
    Config,
    FunctionTunnel,
    StepEvent,
    StreamTunnel,
    Swarm,
    WebhookTunnel,
    WebSocketTunnel,
)


class MockLLM:
    """Fast mock LLM for testing streaming tunnels."""

    async def complete(self, messages, temperature=0.7, max_tokens=1024):
        p = messages[0]["content"]
        if p.startswith("Evaluate"):
            return json.dumps([{"id": 1, "score": 0.9, "critique": "Solid."}])
        return "Tunnel proposal response."


class TestTunnel(unittest.IsolatedAsyncioTestCase):
    """Test suite for StepEvent serialization, StreamTunnel, and Swarm integration."""

    def test_step_event_formatting(self):
        event = StepEvent(
            event_type="step",
            stage="propose",
            agent=0,
            status="ok",
            data="Sample solution",
            seconds=0.45,
            metadata={"role": "Solver"},
        )

        # 1. to_dict
        d = event.to_dict()
        self.assertEqual(d["event_type"], "step")
        self.assertEqual(d["stage"], "propose")
        self.assertEqual(d["agent"], 0)
        self.assertEqual(d["data"], "Sample solution")

        # 2. to_json
        j = event.to_json()
        self.assertIsInstance(j, str)
        parsed = json.loads(j)
        self.assertEqual(parsed["event_type"], "step")

        # 3. to_sse
        sse = event.to_sse()
        self.assertTrue(sse.startswith("event: step\n"))
        self.assertIn("data: ", sse)
        self.assertTrue(sse.endswith("\n\n"))

    async def test_stream_tunnel_lifecycle(self):
        tunnel = StreamTunnel()

        # Send events and close
        async def produce():
            await tunnel.send(
                StepEvent("stage_start", "propose", -1, "ok", "Starting")
            )
            await tunnel.send(
                StepEvent("step", "propose", 0, "ok", "Proposal 0")
            )
            await tunnel.close()

        asyncio.create_task(produce())

        received = []
        async for ev in tunnel:
            received.append(ev)

        self.assertEqual(len(received), 2)
        self.assertEqual(received[0].event_type, "stage_start")
        self.assertEqual(received[1].data, "Proposal 0")

    async def test_stream_tunnel_sse_and_jsonl(self):
        tunnel = StreamTunnel()

        async def produce():
            await tunnel.send(StepEvent("step", "propose", 0, "ok", "Data 1"))
            await tunnel.close()

        asyncio.create_task(produce())

        lines = []
        async for line in tunnel.sse_stream():
            lines.append(line)

        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("event: step\n"))

    async def test_swarm_streaming_with_tunnel(self):
        tunnel = StreamTunnel()
        backend = MockLLM()
        config = Config(agents=2, rounds=0)

        # Run swarm in background with tunnel
        async def run_swarm():
            await Swarm(backend=backend, config=config, tunnel=tunnel).run("Test streaming")

        task = asyncio.create_task(run_swarm())

        events_streamed = []
        async for ev in tunnel:
            events_streamed.append(ev)

        await task

        # Ensure we received stage_start, steps, stage_end, and completed
        event_types = [e.event_type for e in events_streamed]
        self.assertIn("stage_start", event_types)
        self.assertIn("step", event_types)
        self.assertIn("stage_end", event_types)
        self.assertIn("completed", event_types)

        # The last event should be 'completed' with the final answer
        last_event = events_streamed[-1]
        self.assertEqual(last_event.event_type, "completed")
        self.assertEqual(last_event.data, "Tunnel proposal response.")

    async def test_function_tunnel(self):
        events_received = []

        def handle_event(ev: StepEvent):
            events_received.append(ev)

        tunnel = FunctionTunnel(handle_event)
        await tunnel.send(StepEvent("step", "propose", 0, "ok", "Custom func"))
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].data, "Custom func")

    async def test_websocket_tunnel(self):
        mock_ws = MagicMock()
        mock_ws.send_json = MagicMock()

        async def async_send_json(data):
            mock_ws.sent_data = data

        mock_ws.send_json = async_send_json

        tunnel = WebSocketTunnel(mock_ws)
        await tunnel.send(StepEvent("step", "propose", 0, "ok", "WS test"))
        self.assertEqual(mock_ws.sent_data["data"], "WS test")


if __name__ == "__main__":
    unittest.main()
