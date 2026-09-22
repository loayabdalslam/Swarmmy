"""Real-time API Tunnel and event streaming system for Swarmmy."""

from __future__ import annotations

import asyncio
import inspect
import json
import time
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, AsyncIterator, Callable, Coroutine, Union


@dataclass
class StepEvent:
    """Represents a discrete real-time event emitted during swarm execution.

    Attributes:
        event_type: Category ('step', 'stage_start', 'stage_end', 'completed', 'error').
        stage: Current swarm stage ('propose', 'review', 'revise', 'synthesize', 'init').
        agent: Agent index (0, 1, 2... or -1 for synthesizer).
        status: Execution status ('ok' or 'fail').
        data: Payload content (proposal text, reviews, final answer, or error details).
        seconds: Elapsed seconds for this specific step.
        timestamp: Unix epoch timestamp when the event occurred.
        metadata: Additional contextual metadata (roles, scores, etc.).
    """
    event_type: str
    stage: str
    agent: int
    status: str
    data: Any
    seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert StepEvent into a serializable dictionary."""
        return {
            "event_type": self.event_type,
            "stage": self.stage,
            "agent": self.agent,
            "status": self.status,
            "data": self.data,
            "seconds": round(self.seconds, 3),
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize StepEvent into a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_sse(self) -> str:
        """Format as a Server-Sent Events (SSE) message for HTTP streaming."""
        return f"event: {self.event_type}\ndata: {self.to_json()}\n\n"


class BaseTunnel(ABC):
    """Abstract base class for streaming tunnels."""

    @abstractmethod
    async def send(self, event: StepEvent) -> None:
        """Transmit a step event through the tunnel."""
        raise NotImplementedError

    async def close(self) -> None:
        """Signal tunnel closure and flush remaining buffers."""
        pass


class StreamTunnel(BaseTunnel):
    """Asynchronous in-memory queue tunnel for API streaming (FastAPI, SSE, WebSockets).

    Example with FastAPI:
        ```python
        @app.get("/stream")
        async def stream(task: str):
            tunnel = StreamTunnel()
            asyncio.create_task(swarm.run(task, tunnel=tunnel))
            return StreamingResponse(tunnel.sse_stream(), media_type="text/event-stream")
        ```
    """

    def __init__(self, maxsize: int = 0):
        self._queue: asyncio.Queue[StepEvent | None] = asyncio.Queue(maxsize=maxsize)
        self._closed = False

    async def send(self, event: StepEvent) -> None:
        if not self._closed:
            await self._queue.put(event)

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            await self._queue.put(None)  # Sentinel to terminate consumers

    async def __aiter__(self) -> AsyncIterator[StepEvent]:
        """Iterate over events asynchronously until the tunnel closes."""
        while True:
            item = await self._queue.get()
            if item is None:
                break
            yield item

    async def sse_stream(self) -> AsyncIterator[str]:
        """Yield Server-Sent Events (SSE) formatted strings suitable for StreamingResponse."""
        async for event in self:
            yield event.to_sse()

    async def jsonl_stream(self) -> AsyncIterator[str]:
        """Yield newline-delimited JSON (NDJSON/JSONL) strings."""
        async for event in self:
            yield event.to_json() + "\n"


class WebhookTunnel(BaseTunnel):
    """Tunnel that pushes each StepEvent as an HTTP POST request to a webhook URL."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ):
        self.url = url
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self.timeout = timeout

    async def send(self, event: StepEvent) -> None:
        def _post():
            payload = event.to_json().encode("utf-8")
            req = urllib.request.Request(self.url, data=payload, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resp.read()
            except Exception:
                # Webhook failures must not break the swarm execution
                pass

        await asyncio.to_thread(_post)


class WebSocketTunnel(BaseTunnel):
    """Tunnel that pushes StepEvents directly into an active WebSocket connection."""

    def __init__(self, websocket: Any):
        self.websocket = websocket

    async def send(self, event: StepEvent) -> None:
        try:
            if hasattr(self.websocket, "send_json"):
                await self.websocket.send_json(event.to_dict())
            elif hasattr(self.websocket, "send_text"):
                await self.websocket.send_text(event.to_json())
            elif hasattr(self.websocket, "send"):
                res = self.websocket.send(event.to_json())
                if inspect.isawaitable(res):
                    await res
        except Exception:
            pass


CallableEventFn = Union[
    Callable[[StepEvent], None],
    Callable[[StepEvent], Coroutine[Any, Any, None]],
]


class FunctionTunnel(BaseTunnel):
    """Tunnel that forwards StepEvents to any custom synchronous or asynchronous function."""

    def __init__(self, fn: CallableEventFn):
        self._fn = fn
        self._is_async = inspect.iscoroutinefunction(fn)

    async def send(self, event: StepEvent) -> None:
        try:
            if self._is_async:
                await self._fn(event)
            else:
                self._fn(event)
        except Exception:
            pass
