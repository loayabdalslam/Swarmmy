"""Unit tests for real-time rich console printer in Swarmmy."""

import io
import json
import unittest

from swarmmy import (
    Colors,
    Config,
    LivePrinter,
    Swarm,
    TraceEvent,
    run_sync,
)


class TestLivePrinter(unittest.TestCase):
    """Test suite for LivePrinter color formatting and trace event output."""

    def test_printer_events_capture(self):
        stream = io.StringIO()
        printer = LivePrinter(show_content=True, colorize=True, stream=stream)

        # 1. Propose event
        printer(
            TraceEvent(
                stage="propose",
                agent=0,
                ok=True,
                seconds=0.42,
                output="First proposal from Agent 0",
            )
        )

        output = stream.getvalue()
        self.assertIn("STAGE 1: PROPOSALS", output)
        self.assertIn("AGENT 0", output)
        self.assertIn("First proposal from Agent 0", output)

        # 2. Review event with JSON
        stream.truncate(0)
        stream.seek(0)
        review_json = json.dumps([
            {"id": 1, "score": 0.85, "critique": "Insightful, but check edge cases."}
        ])
        printer(
            TraceEvent(
                stage="review",
                agent=0,
                ok=True,
                seconds=0.25,
                output=review_json,
            )
        )

        review_output = stream.getvalue()
        self.assertIn("STAGE 2: PEER REVIEWS", review_output)
        self.assertIn("Review for", review_output)
        self.assertIn("0.85", review_output)
        self.assertIn("Insightful, but check edge cases.", review_output)

        # 3. Failed event
        stream.truncate(0)
        stream.seek(0)
        printer(
            TraceEvent(
                stage="revise",
                agent=1,
                ok=False,
                seconds=0.10,
                error="TimeoutError",
            )
        )
        fail_output = stream.getvalue()
        self.assertIn("FAIL", fail_output)
        self.assertIn("TimeoutError", fail_output)

    def test_live_swarm_integration(self):
        stream = io.StringIO()
        printer = LivePrinter(show_content=True, colorize=False, stream=stream)

        def mock_llm(messages, **kwargs):
            p = messages[0]["content"]
            if p.startswith("Evaluate"):
                return json.dumps([{"id": 1, "score": 0.9, "critique": "Solid."}])
            return "Test candidate response"

        # Initialize Swarm with live printer stream
        swarm = Swarm(backend=mock_llm, config=Config(agents=2, rounds=0), on_event=printer)
        result = swarm.run_sync("Test real-time printer")

        self.assertEqual(result.calls, 5)
        console_text = stream.getvalue()
        self.assertIn("STAGE 1: PROPOSALS", console_text)
        self.assertIn("FINAL STAGE: SYNTHESIS", console_text)
        self.assertIn("Test candidate response", console_text)


if __name__ == "__main__":
    unittest.main()
