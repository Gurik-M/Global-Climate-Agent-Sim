"""Citizens agent: households, consumers, public opinion."""

from simulation.models import CITIZENS_OUTPUT_KEYS

NAME = "citizens"
OUTPUT_KEYS = CITIZENS_OUTPUT_KEYS

PROMPT_FRAGMENT = """1. **citizens**: public_pressure_climate (0–1), transition_tolerance, cost_sensitivity, social_demand_adaptation_vs_mitigation. Represents households, consumers, and public pressure for climate action."""
