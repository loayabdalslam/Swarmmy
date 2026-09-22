"""Command-line interface for Swarmmy with multi-provider support."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from . import __version__
from .core import Config, Swarm
from .providers import PROVIDER_REGISTRY, create_provider
from .types import TraceEvent

DEFAULT_PROVIDER_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.3-70b-versatile",
    "deepseek": "deepseek-chat",
    "ollama": "llama3:latest",
    "mistral": "mistral-large-latest",
    "cohere": "command-r-plus-08-2024",
    "openrouter": "meta-llama/llama-3.3-70b-instruct",
}


def main() -> None:
    """Entry point for the swarmmy command-line tool."""
    parser = argparse.ArgumentParser(
        prog="swarmmy",
        description="Swarmmy: Bounded peer-review swarm orchestration for instruction models.",
    )
    parser.add_argument("task", nargs="?", help="Task or prompt to process with the swarm")
    parser.add_argument(
        "--provider", "--backend",
        dest="provider",
        choices=list(sorted(PROVIDER_REGISTRY.keys())),
        default="api",
        help="LLM provider (e.g. openai, anthropic, gemini, groq, deepseek, ollama, mistral, cohere, openrouter, hf, api)",
    )
    parser.add_argument(
        "--model",
        default="",
        help="Model name or identifier (defaults to standard recommended model for the provider)",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="Custom base URL for API endpoint",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="API key (optional; defaults to provider's environment variable)",
    )
    parser.add_argument("--agents", type=int, default=4, help="Number of peer agents (default: 4)")
    parser.add_argument("--rounds", type=int, default=1, help="Review and revision rounds (default: 1)")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Concurrency limit for model requests (default: 4)",
    )
    parser.add_argument(
        "--max-calls",
        type=int,
        default=40,
        help="Maximum total API calls budget (default: 40)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum generated tokens per response (default: 1024)",
    )
    parser.add_argument(
        "--peer-chars",
        type=int,
        default=3000,
        help="Character limit per peer candidate in reviews (default: 3000)",
    )
    parser.add_argument(
        "--roles",
        default=None,
        help="Role preset ('default', 'code', 'creative') or comma-separated custom roles",
    )
    parser.add_argument(
        "--output",
        default="swarmmy-result.json",
        help="Path to save execution trace and results JSON (default: swarmmy-result.json)",
    )
    parser.add_argument(
        "--rpm",
        type=int,
        default=None,
        help="Rate limit: maximum requests per minute (throttling)",
    )
    parser.add_argument(
        "--max-total-tokens",
        type=int,
        default=None,
        help="Hard ceiling on total tokens consumed across all calls",
    )
    parser.add_argument(
        "--max-cost",
        type=float,
        default=None,
        help="Hard ceiling on estimated financial cost in USD",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries when encountering HTTP 429 Too Many Requests (default: 3)",
    )
    parser.add_argument(
        "-l", "--live",
        action="store_true",
        help="Display real-time rich colored output from each agent, round, and stage",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show live progress logs during execution",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Swarmmy {__version__}",
        help="Show program's version number and exit",
    )

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        sys.exit(1)

    provider_name = args.provider.lower()
    model = args.model
    if not model:
        model = DEFAULT_PROVIDER_MODELS.get(provider_name, "")

    if not model and provider_name in ("api", "openai-compatible", "hf", "huggingface"):
        sys.stderr.write(f"Error: --model argument is required for provider '{provider_name}'.\n")
        sys.exit(2)

    roles_arg = args.roles
    if roles_arg and "," in roles_arg:
        roles_arg = [r.strip() for r in roles_arg.split(",") if r.strip()]

    config = Config(
        agents=args.agents,
        rounds=args.rounds,
        concurrency=args.concurrency,
        max_calls=args.max_calls,
        max_tokens=args.max_tokens,
        peer_chars=args.peer_chars,
        roles=roles_arg,
        rpm=args.rpm,
        max_total_tokens=args.max_total_tokens,
        max_cost_usd=args.max_cost,
        max_retries=args.max_retries,
    )

    try:
        backend = create_provider(
            provider=provider_name,
            model=model or None,
            api_key=args.api_key,
            base_url=args.base_url,
        )
    except Exception as exc:
        sys.stderr.write(f"Failed to initialize provider '{provider_name}': {exc}\n")
        sys.exit(2)

    from .printer import LivePrinter

    event_hook = None
    if args.live:
        event_hook = LivePrinter(show_content=True)
    elif args.verbose:
        def on_event(event: TraceEvent) -> None:
            status = "OK" if event.ok else "FAIL"
            print(
                f"[{status:<4}] Stage: {event.stage:<10} | Agent: {event.agent:<2} | {event.seconds:.2f}s "
                f"{f'({event.error})' if event.error else ''}"
            )
        event_hook = on_event

    swarm = Swarm(backend=backend, config=config, on_event=event_hook)
    result = asyncio.run(swarm.run(args.task))

    Path(args.output).write_text(result.to_json(indent=2), encoding="utf-8")

    print("\n" + "=" * 50)
    print("FINAL SWARM ANSWER:")
    print("=" * 50)
    print(result.answer)
    print("=" * 50)
    print(f"Total calls: {result.calls} | Elapsed: {result.elapsed_seconds:.2f}s | Saved: {args.output}")
    u = result.usage
    print(
        f"Usage: {u.total_tokens} tokens (in: {u.prompt_tokens}, out: {u.completion_tokens}) "
        f"| Est. Cost: ${u.estimated_cost_usd:.4f} USD"
    )
    if u.rate_limit_waits_seconds > 0:
        print(f"Rate limit throttling wait: {u.rate_limit_waits_seconds:.2f}s ({u.retries_attempted} retries)")
    if result.warnings:
        print(f"Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
