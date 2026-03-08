"""Governance agent: regional policy direction (acts after the other five agents)."""

# Keys match PolicyPackage in models.py
OUTPUT_KEYS = [
    "climate_policy_strength",
    "fossil_policy_stance",
    "industrial_regulation_level",
    "efficiency_infrastructure_policy",
    "land_use_enforcement",
    "agriculture_incentives",
    "carbon_removal_investment",
    "international_climate_cooperation",
]

NAME = "governance"

PROMPT_FRAGMENT = """6. **governance** (chosen after the other 5, using their signals): climate_policy_strength, fossil_policy_stance, industrial_regulation_level, efficiency_infrastructure_policy, land_use_enforcement, agriculture_incentives, carbon_removal_investment, international_climate_cooperation. Represents overall regional policy package."""
