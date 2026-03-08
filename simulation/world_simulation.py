"""
WorldSimulation: 7 regional blocs, one LLM call per decade, global emissions aggregation.
"""

from simulation.region import Region
from simulation.initial_state import REGIONAL_BLOCS, initial_state_for_region
from simulation.models import EMISSION_SECTORS
from simulation.agents.batch import run_batch_agents


class WorldSimulation:
    """
    Global coupled socio-climate simulation.
    One LLM call per decade produces all region/agent outputs; then emissions are computed and aggregated.
    """

    def __init__(self):
        self.regions: list[Region] = []
        for name in REGIONAL_BLOCS:
            profile = {"name": name}
            state = initial_state_for_region(name)
            self.regions.append(Region(name=name, profile=profile, state=state))
        self.decade = 0
        self.global_emissions_history: list[dict] = []

    def step_decade(self) -> dict:
        """
        Run one decade: one batch LLM call for all regions/agents,
        then compute emissions per region and aggregate globally.
        """
        region_states = [(r.name, r.state) for r in self.regions]
        all_outputs = run_batch_agents(region_states)
        for region in self.regions:
            region.step_from_outputs(all_outputs[region.name])

        global_by_sector = self._aggregate_global_emissions()
        self.global_emissions_history.append(global_by_sector)
        self.decade += 1
        self._evolve_state(global_by_sector)
        return global_by_sector

    def _aggregate_global_emissions(self) -> dict:
        """E_global_by_sector = sum over regions (approach.md Step 4)."""
        total = {sector: 0.0 for sector in EMISSION_SECTORS}
        for region in self.regions:
            d = region.emissions.to_dict()
            for sector in EMISSION_SECTORS:
                total[sector] += d.get(sector, 0.0)
        total["decade"] = self.decade
        return total

    def _evolve_state(self, global_emissions: dict) -> None:
        """Update region state for next decade (bounded rates; placeholder for climate model)."""
        total_emissions = sum(
            v for k, v in global_emissions.items() if k != "decade" and isinstance(v, (int, float))
        )
        delta_damage = min(0.1, 0.02 * (total_emissions or 0.1))
        for region in self.regions:
            d = region.state.get("climate_damage", 0.0)
            region.state["climate_damage"] = min(1.0, d + delta_damage)
