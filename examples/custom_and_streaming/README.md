# 🛠️ Custom Callables & Live Streaming Guide & Examples

Swarmmy is completely open and agnostic: you can plug in **any custom Python function**, third-party SDK (LiteLLM, LangChain, proprietary fine-tuned model endpoints), or stream real-time events over **Server-Sent Events (SSE)** or WebSockets.

---

## 📁 Examples in this Directory

1. **[`01_custom_callable_llm.py`](01_custom_callable_llm.py)**: How to wrap any arbitrary Python function, LiteLLM wrapper, or offline mock as a Swarmmy provider.
2. **[`02_fastapi_sse_streaming.py`](02_fastapi_sse_streaming.py)**: Exposing a real-time Server-Sent Events (SSE) endpoint with FastAPI so web frontends can stream each agent's proposal and review live.
3. **[`03_event_hooks_and_tracing.py`](03_event_hooks_and_tracing.py)**: Hooking into Swarmmy's lifecycle event pipeline (`on_event`) for metrics, custom terminal logging, or APM monitoring (Datadog/NewRelic).
