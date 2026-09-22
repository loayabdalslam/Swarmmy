"""Data structures and type definitions for Swarmmy."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Coroutine, Union


@dataclass
class Candidate:
    """Represents a solution proposal produced by an agent."""
    id: int
    text: str
    peer_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Review:
    """Represents a peer review evaluation from one agent to another."""
    reviewer: int
    id: int
    score: float
    critique: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    """Represents a single step in the orchestration execution trace."""
    stage: str
    agent: int
    ok: bool
    seconds: float
    output: str | None = None
    error: str | None = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


from .limits import UsageReport


@dataclass
class Result:
    """Comprehensive result object returned by Swarm execution."""
    answer: str
    candidates: list[Candidate]
    reviews: list[Review]
    trace: list[TraceEvent]
    calls: int
    elapsed_seconds: float
    warnings: list[str]
    usage: UsageReport = field(default_factory=UsageReport)

    def to_dict(self) -> dict[str, Any]:
        """Convert Result into a serializable dictionary."""
        return {
            "answer": self.answer,
            "candidates": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.candidates],
            "reviews": [r.to_dict() if hasattr(r, "to_dict") else r for r in self.reviews],
            "trace": [t.to_dict() if hasattr(t, "to_dict") else t for t in self.trace],
            "calls": self.calls,
            "elapsed_seconds": self.elapsed_seconds,
            "warnings": list(self.warnings),
            "usage": self.usage.to_dict() if hasattr(self.usage, "to_dict") else self.usage,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert Result into a formatted JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# Callback type signatures for observing swarm progress
SyncCallback = Callable[[TraceEvent], None]
AsyncCallback = Callable[[TraceEvent], Coroutine[Any, Any, None]]
ProgressHook = Union[SyncCallback, AsyncCallback]
