"""Industry agent: manufacturing, firms, industrial incumbents."""

from simulation.models import INDUSTRY_OUTPUT_KEYS

NAME = "industry"
OUTPUT_KEYS = INDUSTRY_OUTPUT_KEYS

PROMPT_FRAGMENT = """2. **industry**: lobbying_strength, clean_investment_level, industrial_emissions_intensity, resistance_to_regulation. Represents manufacturing and industrial decarbonization vs fossil lock-in."""
