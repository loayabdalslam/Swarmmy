"""Backward-compatibility shim for legacy instruct_swarm imports.

Please migrate to importing from 'swarmmy' directly:
    from swarmmy import Swarm, Config, Result, OpenAICompatible, HuggingFace
"""

import warnings
from swarmmy import (
    Config,
    HuggingFace,
    OpenAICompatible,
    Result,
    Swarm,
)

warnings.warn(
    "The 'instruct_swarm' package name is deprecated and will be removed in a future release. "
    "Please update your imports to 'swarmmy'.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Swarm", "Config", "Result", "OpenAICompatible", "HuggingFace"]
