"""International Relations agent: diplomacy, cooperation, trade pressure."""

from simulation.models import INTERNATIONAL_OUTPUT_KEYS

NAME = "international"
OUTPUT_KEYS = INTERNATIONAL_OUTPUT_KEYS

PROMPT_FRAGMENT = """5. **international**: climate_cooperation_level (0–1), norm_sensitivity, trade_diplomatic_pressure_exerted, reputation_effect. Represents diplomacy, peer norms, and trade/diplomatic leverage."""
