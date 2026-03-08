"""Multi-agent definitions: each agent has its own module; batch composes them in one LLM call."""

from .base import call_llm

# Order: non-governance first, governance last (so prompt describes governance as "chosen after the other 5")
from . import citizens, industry, energy, land_use, international, governance

AGENTS = [citizens, industry, energy, land_use, international, governance]

from .batch import run_batch_agents

__all__ = [
    "call_llm",
    "run_batch_agents",
    "AGENTS",
    "citizens",
    "industry",
    "energy",
    "land_use",
    "international",
    "governance",
]
