"""
Compute sector-level emissions from regional state and agent outputs.

All formulas are interpretable and endogenous (approach.md §5).
Emissions are in arbitrary units before global calibration; global output uses MtCO2e-style blend then ratio to 1990.
"""

from simulation.models import EmissionsProfile, PolicyPackage, EMISSION_SECTORS


def _get(d: dict, key: str, default: float = 0.5) -> float:
    v = d.get(key, default)
    return max(0.0, min(1.0, float(v))) if v is not None else default


def compute_emissions(
    state: dict,
    policy: PolicyPackage,
    citizens: dict,
    industry: dict,
    energy: dict,
    land_use: dict,
    region_scale: float = 1.0,
) -> EmissionsProfile:
    """
    Compute emissions for all 7 sectors from state and agent outputs.
    region_scale: optional scaling by region size (e.g. population or GDP share).
    """
    # Energy & heat: energy_demand, fossil share, clean share, climate ambition, fossil restriction
    energy_demand = _get(state, "energy_demand")
    fossil_share = _get(energy, "energy_mix_fossil_share")
    climate_strength = policy.climate_policy_strength
    fossil_stance = policy.fossil_policy_stance  # 1 = restrictive
    energy_heat = (
        region_scale
        * energy_demand
        * fossil_share
        * (1.0 - 0.5 * climate_strength - 0.3 * fossil_stance)
    )

    # Transport: transport_demand, electrification support, urbanization, transition tolerance, policy
    transport_demand = _get(state, "transport_demand")
    electrification = _get(energy, "electrification_support_capacity")
    transition_tolerance = _get(citizens, "transition_tolerance")
    transport = (
        region_scale
        * transport_demand
        * (1.0 - 0.4 * electrification - 0.2 * transition_tolerance)
        * (1.0 - 0.3 * policy.efficiency_infrastructure_policy)
    )

    # Buildings: building_demand, efficiency policy, energy mix, quality of life, electrification
    building_demand = _get(state, "building_demand")
    efficiency = policy.efficiency_infrastructure_policy
    transport_buildings = (
        region_scale
        * building_demand
        * (0.5 + 0.5 * fossil_share)
        * (1.0 - 0.4 * efficiency)
        * (1.0 - 0.2 * electrification)
    )

    # Manufacturing & industry: industrial_intensity, industrial_emissions_intensity, regulation, innovation, lobbying
    ind_intensity = _get(state, "industrial_intensity")
    ind_emissions = _get(industry, "industrial_emissions_intensity")
    regulation = policy.industrial_regulation_level
    innovation = _get(state, "innovation_capacity")
    lobbying = _get(industry, "lobbying_strength")
    industry_emissions = (
        region_scale
        * ind_intensity
        * ind_emissions
        * (1.0 - 0.4 * regulation + 0.2 * lobbying)
        * (1.0 - 0.2 * innovation)
    )

    # Deforestation: land pressure, land-use enforcement, development pressure, reforestation
    land_pressure = _get(state, "land_use_pressure")
    enforcement = policy.land_use_enforcement
    deforestation_rate = _get(land_use, "deforestation_rate")
    reforestation = _get(land_use, "reforestation_conservation_level")
    deforestation = (
        region_scale
        * land_pressure
        * deforestation_rate
        * (1.0 - 0.5 * enforcement)
        * (1.0 - 0.4 * reforestation)
    )

    # Agriculture: agriculture_intensity, climate_damage, agricultural reform, land-use pressure
    ag_intensity = _get(state, "agriculture_intensity")
    ag_emissions = _get(land_use, "agricultural_emissions_intensity")
    ag_incentives = policy.agriculture_incentives
    agriculture = (
        region_scale
        * ag_intensity
        * ag_emissions
        * (1.0 - 0.3 * ag_incentives)
    )

    # Carbon removal: governance investment, innovation capacity, institutional capacity (negative = removal)
    removal_invest = policy.carbon_removal_investment
    innovation_cap = _get(state, "innovation_capacity")
    # Proxy institutional capacity via political_stability
    inst_cap = _get(state, "political_stability")
    carbon_removal = -region_scale * (
        0.5 * removal_invest + 0.3 * innovation_cap + 0.2 * inst_cap
    )

    return EmissionsProfile(
        energy_heat=max(0.0, energy_heat),
        transport=max(0.0, transport),
        buildings=max(0.0, transport_buildings),
        industry=max(0.0, industry_emissions),
        deforestation=max(0.0, deforestation),
        agriculture=max(0.0, agriculture),
        carbon_removal=carbon_removal,
    )
