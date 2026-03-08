"""
Initialize region state from profile-specific priors (approach.md §6).
All values are normalized ~0–1 for use in equations; population and GDP can be in real units.
"""


def default_state() -> dict:
    """Base state with all required keys at 0.5."""
    return {
        "population": 0.5,
        "gdp": 0.5,
        "gdp_per_capita": 0.5,
        "quality_of_life": 0.5,
        "political_stability": 0.5,
        "political_polarization": 0.5,
        "climate_vulnerability": 0.5,
        "international_perception": 0.5,
        "public_policy_responsiveness": 0.5,
        "innovation_capacity": 0.5,
        "fossil_legacy": 0.5,
        "industrial_intensity": 0.5,
        "energy_demand": 0.5,
        "transport_demand": 0.5,
        "building_demand": 0.5,
        "land_use_pressure": 0.5,
        "agriculture_intensity": 0.5,
        "climate_damage": 0.0,
        "trade_diplomatic_influence": 0.5,
    }


def initial_state_for_region(region_name: str) -> dict:
    """Region-specific initial state from approach.md §6."""
    s = default_state()
    region_name = region_name.lower()

    if "north america" in region_name or region_name == "north america":
        s["gdp_per_capita"] = 0.85
        s["transport_demand"] = 0.8
        s["building_demand"] = 0.8
        s["fossil_legacy"] = 0.75
        s["innovation_capacity"] = 0.85
        s["public_policy_responsiveness"] = 0.7
        s["political_polarization"] = 0.65
        s["industrial_intensity"] = 0.7

    elif "europe" in region_name or region_name == "europe":
        s["climate_vulnerability"] = 0.4  # lower = more policy responsiveness in our scale
        s["international_perception"] = 0.8
        s["innovation_capacity"] = 0.75
        s["fossil_legacy"] = 0.45
        s["population"] = 0.4

    elif "africa" in region_name or region_name == "africa":
        s["gdp_per_capita"] = 0.25
        s["climate_vulnerability"] = 0.85
        s["public_policy_responsiveness"] = 0.35
        s["innovation_capacity"] = 0.35
        s["trade_diplomatic_influence"] = 0.35
        s["climate_damage"] = 0.3

    elif "south america" in region_name or region_name == "south america":
        s["land_use_pressure"] = 0.8
        s["agriculture_intensity"] = 0.75
        s["climate_vulnerability"] = 0.6
        s["gdp_per_capita"] = 0.5
        s["political_stability"] = 0.5

    elif "southeast asia" in region_name or region_name == "southeast asia":
        s["energy_demand"] = 0.8
        s["industrial_intensity"] = 0.75
        s["transport_demand"] = 0.7
        s["climate_vulnerability"] = 0.7

    elif "asia major" in region_name or region_name == "asia major":
        s["population"] = 0.95
        s["industrial_intensity"] = 0.9
        s["energy_demand"] = 0.9
        s["trade_diplomatic_influence"] = 0.85
        s["public_policy_responsiveness"] = 0.5
        s["political_stability"] = 0.55

    elif "australia" in region_name or region_name == "australia":
        s["gdp_per_capita"] = 0.85
        s["innovation_capacity"] = 0.75
        s["fossil_legacy"] = 0.7
        s["climate_vulnerability"] = 0.7
        s["population"] = 0.2

    return s


# Official list of 7 regional blocs (approach.md)
REGIONAL_BLOCS = [
    "North America",
    "Europe",
    "Africa",
    "South America",
    "Southeast Asia",
    "Asia Major",
    "Australia",
]
