"""Energy agent: energy supply system, grid, fuels."""

from simulation.models import ENERGY_OUTPUT_KEYS

NAME = "energy"
OUTPUT_KEYS = ENERGY_OUTPUT_KEYS

PROMPT_FRAGMENT = """3. **energy**: energy_mix_fossil_share, grid_decarbonization_pace, fossil_lock_in_level, electrification_support_capacity. Represents electricity and fuel supply, fossil vs low-carbon mix."""
