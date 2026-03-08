"""Land Use agent: agriculture, forests, land conversion, food system."""

from simulation.models import LAND_USE_OUTPUT_KEYS

NAME = "land_use"
OUTPUT_KEYS = LAND_USE_OUTPUT_KEYS

PROMPT_FRAGMENT = """4. **land_use**: deforestation_rate, agricultural_emissions_intensity, reforestation_conservation_level, land_use_transition_pressure. Represents agriculture, forests, and land-use emissions."""
