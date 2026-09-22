"""Real-time rich colored console printer for Swarmmy."""

from __future__ import annotations

import json
import os
import sys
import threading
from typing import Any

from .types import TraceEvent

# Ensure UTF-8 output on modern Python (3.7+)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Enable ANSI escape sequences on Windows consoles
if os.name == "nt":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        os.system("")


class Colors:
    """ANSI color codes for terminal formatting."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground standard
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Backgrounds
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_DARK = "\033[100m"


AGENT_PALETTE = [
    Colors.BRIGHT_CYAN,
    Colors.BRIGHT_GREEN,
    Colors.BRIGHT_YELLOW,
    Colors.BRIGHT_MAGENTA,
    Colors.BRIGHT_BLUE,
    Colors.BRIGHT_RED,
]


class LivePrinter:
    """Thread-safe, real-time rich console printer with per-agent colors and stage banners.

    Example:
        ```python
        from swarmmy import Swarm, LivePrinter

        swarm = Swarm(backend, on_event=LivePrinter())
        # Or simply:
        swarm = Swarm(backend, live=True)
        ```
    """

    def __init__(
        self,
        show_content: bool = True,
        max_chars: int = 2000,
        colorize: bool = True,
        stream=None,
    ):
        self.show_content = show_content
        self.max_chars = max_chars
        self.colorize = colorize
        self.stream = stream or sys.stdout
        self._lock = threading.Lock()
        self._last_stage: str | None = None

    def _c(self, code: str) -> str:
        return code if self.colorize else ""

    def _agent_color(self, agent_id: int) -> str:
        if not self.colorize:
            return ""
        if agent_id < 0:
            return Colors.BOLD + Colors.BRIGHT_WHITE
        return AGENT_PALETTE[agent_id % len(AGENT_PALETTE)]

    def _write(self, text: str) -> None:
        """Write string to stream with Unicode encoding error recovery."""
        try:
            self.stream.write(text)
        except UnicodeEncodeError:
            encoding = getattr(self.stream, "encoding", "ascii") or "ascii"
            safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
            self.stream.write(safe_text)
        self.stream.flush()

    def print_stage_header(self, stage: str) -> None:
        """Print a visually distinct banner when transitioning to a new swarm stage."""
        c_reset = self._c(Colors.RESET)
        c_bold = self._c(Colors.BOLD)
        c_cyan = self._c(Colors.BRIGHT_CYAN)
        c_yellow = self._c(Colors.BRIGHT_YELLOW)
        c_magenta = self._c(Colors.BRIGHT_MAGENTA)
        c_green = self._c(Colors.BRIGHT_GREEN)

        titles = {
            "propose": (c_cyan, "STAGE 1: PROPOSALS", "Independent solutions generated across diverse roles"),
            "review": (c_yellow, "STAGE 2: PEER REVIEWS", "Cross-evaluating peer solutions (no self-grading)"),
            "revise": (c_magenta, "STAGE 3: REVISIONS", "Iterative refinement addressing peer feedback"),
            "synthesize": (c_green, "FINAL STAGE: SYNTHESIS", "Integrating top insights into unified answer"),
        }

        color, title, desc = titles.get(stage, (c_bold, f"STAGE: {stage.upper()}", ""))
        width = 72
        line = "=" * width

        self._write(
            f"\n{color}{line}\n"
            f"{c_bold}  >>> {title} <<<\n"
            f"{self._c(Colors.DIM)}      {desc}{c_reset}\n"
            f"{color}{line}{c_reset}\n\n"
        )

    def __call__(self, event: TraceEvent) -> None:
        """Handle trace event synchronously with immediate colored console output."""
        with self._lock:
            # Check if stage changed to print a banner
            if event.stage != self._last_stage:
                self._last_stage = event.stage
                self.print_stage_header(event.stage)

            c_reset = self._c(Colors.RESET)
            c_bold = self._c(Colors.BOLD)
            c_dim = self._c(Colors.DIM)
            c_agent = self._agent_color(event.agent)

            agent_label = "SYNTHESIZER" if event.agent < 0 else f"AGENT {event.agent}"
            status_badge = (
                f"{self._c(Colors.BRIGHT_GREEN)}[OK]{c_reset}"
                if event.ok
                else f"{self._c(Colors.BRIGHT_RED)}[FAIL: {event.error}]{c_reset}"
            )

            # Header Line
            header = (
                f"{c_agent}{c_bold}┌─ {agent_label}{c_reset} "
                f"{c_dim}({event.stage.upper()} | {event.seconds:.2f}s){c_reset} "
                f"{status_badge} "
            )
            padding_len = max(0, 70 - len(f"┌─ {agent_label} ({event.stage.upper()} | {event.seconds:.2f}s) [OK] "))
            header += f"{c_agent}{'─' * padding_len}┐{c_reset}"

            self._write(f"{header}\n")

            # Content display
            if self.show_content and event.ok and event.output:
                output = event.output.strip()
                if event.stage == "review":
                    try:
                        reviews = json.loads(output)
                        if isinstance(reviews, list):
                            for r in reviews:
                                score_val = r.get("score", 0.0)
                                stars = "★" * int(round(score_val * 5)) + "☆" * (5 - int(round(score_val * 5)))
                                critique = r.get("critique", "").strip()
                                self._write(
                                    f"{c_agent}│{c_reset}   🎯 Review for {c_bold}Agent {r.get('id')}{c_reset}: "
                                    f"Score: {self._c(Colors.BRIGHT_YELLOW)}{score_val:.2f}{c_reset} "
                                    f"({stars})\n"
                                    f"{c_agent}│{c_reset}      {c_dim}\"{critique}\"{c_reset}\n"
                                )
                        else:
                            self._print_indented(output, c_agent, c_dim, c_reset)
                    except Exception:
                        self._print_indented(output, c_agent, c_dim, c_reset)
                else:
                    self._print_indented(output, c_agent, "", c_reset)
            elif not event.ok:
                self._write(
                    f"{c_agent}│{c_reset}   {self._c(Colors.BRIGHT_RED)}Execution failed: {event.error}{c_reset}\n"
                )

            # Footer Line
            self._write(f"{c_agent}└{'─' * 70}┘{c_reset}\n\n")

    def _print_indented(self, text: str, c_agent: str, c_style: str, c_reset: str) -> None:
        """Print multiline text with aligned borders and character capping."""
        if self.max_chars and len(text) > self.max_chars:
            text = text[: self.max_chars] + f"\n... [truncated, {len(text)} chars total]"

        for line in text.splitlines():
            self._write(f"{c_agent}│{c_reset}   {c_style}{line}{c_reset}\n")
