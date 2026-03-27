"""State, policy, and emissions data structures for the simulation."""

from dataclasses import dataclass, field
from typing import TypedDict


# --- Region state schema (approach.md §4) ---

class RegionState(TypedDict, total=False):
    population: float
    gdp: float
    gdp_per_capita: float
    quality_of_life: float
    political_stability: float
    political_polarization: float
    climate_vulnerability: float
    international_perception: float
    public_policy_responsiveness: float
    innovation_capacity: float
    fossil_legacy: float
    industrial_intensity: float
    energy_demand: float
    transport_demand: float
    building_demand: float
    land_use_pressure: float
    agriculture_intensity: float
    climate_damage: float
    trade_diplomatic_influence: float


# --- Policy package (Governance agent outputs) ---

@dataclass
class PolicyPackage:
    climate_policy_strength: float
    fossil_policy_stance: float
    industrial_regulation_level: float
    efficiency_infrastructure_policy: float
    land_use_enforcement: float
    agriculture_incentives: float
    carbon_removal_investment: float
    international_climate_cooperation: float

    @classmethod
    def from_dict(cls, d: dict) -> "PolicyPackage":
        return cls(
            climate_policy_strength=float(d.get("climate_policy_strength", 0.5)),
            fossil_policy_stance=float(d.get("fossil_policy_stance", 0.5)),
            industrial_regulation_level=float(d.get("industrial_regulation_level", 0.5)),
            efficiency_infrastructure_policy=float(d.get("efficiency_infrastructure_policy", 0.5)),
            land_use_enforcement=float(d.get("land_use_enforcement", 0.5)),
            agriculture_incentives=float(d.get("agriculture_incentives", 0.5)),
            carbon_removal_investment=float(d.get("carbon_removal_investment", 0.5)),
            international_climate_cooperation=float(d.get("international_climate_cooperation", 0.5)),
        )

    def to_dict(self) -> dict:
        return {
            "climate_policy_strength": self.climate_policy_strength,
            "fossil_policy_stance": self.fossil_policy_stance,
            "industrial_regulation_level": self.industrial_regulation_level,
            "efficiency_infrastructure_policy": self.efficiency_infrastructure_policy,
            "land_use_enforcement": self.land_use_enforcement,
            "agriculture_incentives": self.agriculture_incentives,
            "carbon_removal_investment": self.carbon_removal_investment,
            "international_climate_cooperation": self.international_climate_cooperation,
        }


# --- Agent outputs (dicts for flexibility; keys per approach.md) ---

# Citizens
CITIZENS_OUTPUT_KEYS = [
    "public_pressure_climate",
    "transition_tolerance",
    "cost_sensitivity",
    "social_demand_adaptation_vs_mitigation",
]

# Industry
INDUSTRY_OUTPUT_KEYS = [
    "lobbying_strength",
    "clean_investment_level",
    "industrial_emissions_intensity",
    "resistance_to_regulation",
]

# Energy
ENERGY_OUTPUT_KEYS = [
    "energy_mix_fossil_share",
    "grid_decarbonization_pace",
    "fossil_lock_in_level",
    "electrification_support_capacity",
]

# Land Use
LAND_USE_OUTPUT_KEYS = [
    "deforestation_rate",
    "agricultural_emissions_intensity",
    "reforestation_conservation_level",
    "land_use_transition_pressure",
]

# International Relations
INTERNATIONAL_OUTPUT_KEYS = [
    "climate_cooperation_level",
    "norm_sensitivity",
    "trade_diplomatic_pressure_exerted",
    "reputation_effect",
]


# --- Emissions profile (sector-level, per region and globally) ---

EMISSION_SECTORS = [
    "energy_heat",
    "transport",
    "buildings",
    "industry",
    "deforestation",
    "agriculture",
    "carbon_removal",
]


@dataclass
class EmissionsProfile:
    """Sector-level emissions (arbitrary units before global calibration)."""
    energy_heat: float = 0.0
    transport: float = 0.0
    buildings: float = 0.0
    industry: float = 0.0
    deforestation: float = 0.0
    agriculture: float = 0.0
    carbon_removal: float = 0.0  # negative = removal

    def to_dict(self) -> dict:
        return {
            "energy_heat": self.energy_heat,
            "transport": self.transport,
            "buildings": self.buildings,
            "industry": self.industry,
            "deforestation": self.deforestation,
            "agriculture": self.agriculture,
            "carbon_removal": self.carbon_removal,
        }

    def total_net(self) -> float:
        return (
            self.energy_heat + self.transport + self.buildings
            + self.industry + self.deforestation + self.agriculture
            + self.carbon_removal
        )
