"""Predefined and customizable role prompts for Swarmmy agents."""

from __future__ import annotations

from typing import Sequence

DEFAULT_ROLES: tuple[str, ...] = (
    "Solve directly and state assumptions.",
    "Explore a different approach.",
    "Look for counterexamples and edge cases.",
    "Prioritize practical implementation.",
    "Check evidence and unsupported claims.",
    "Simplify and check consistency.",
)

CODE_REVIEW_ROLES: tuple[str, ...] = (
    "Focus on algorithmic efficiency, time/space complexity, and scalability.",
    "Focus on edge cases, boundary values, error handling, and resilience.",
    "Focus on maintainability, readability, modularity, and clean architecture.",
    "Focus on security vulnerabilities, data sanitization, and attack surfaces.",
)

CREATIVE_ROLES: tuple[str, ...] = (
    "Propose conventional, well-established industry best practices.",
    "Propose radical, innovative, out-of-the-box approaches.",
    "Focus on user experience, clarity, and ergonomic simplicity.",
    "Play devil's advocate, rigorously challenging common assumptions.",
)

ROLE_PRESETS: dict[str, tuple[str, ...]] = {
    "default": DEFAULT_ROLES,
    "code": CODE_REVIEW_ROLES,
    "creative": CREATIVE_ROLES,
}


def resolve_roles(roles: str | Sequence[str] | None = None) -> tuple[str, ...]:
    """Resolve role configuration into a sequence of role instructions.

    Args:
        roles: Preset name ("default", "code", "creative") or a custom list of role strings.

    Returns:
        A tuple of role prompt strings.
    """
    if roles is None:
        return DEFAULT_ROLES
    if isinstance(roles, str):
        preset = roles.lower()
        if preset in ROLE_PRESETS:
            return ROLE_PRESETS[preset]
        raise ValueError(
            f"Unknown role preset '{roles}'. Available presets: {list(ROLE_PRESETS.keys())}"
        )
    resolved = tuple(str(r).strip() for r in roles if str(r).strip())
    if not resolved:
        raise ValueError("Roles sequence cannot be empty")
    return resolved
