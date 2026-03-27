"""
WorldSimulation: 7 regional blocs, one LLM call per 5-year step, global emissions aggregation.
"""

from simulation.region import Region
from simulation.initial_state import REGIONAL_BLOCS, initial_state_for_region
from simulation.models import EMISSION_SECTORS
from simulation.agents.batch import run_batch_agents
from simulation.emission_calibration import (
    YEARS_PER_STEP,
    blend_raw_with_empirical,
    ratio_to_1990_baseline,
    year_for_step,
)


class WorldSimulation:
    """
    Global coupled socio-climate simulation.
    One LLM call per timestep produces all region/agent outputs; then emissions are computed and aggregated.
    """

    def __init__(self):
        self.regions: list[Region] = []
        for name in REGIONAL_BLOCS:
            profile = {"name": name}
            state = initial_state_for_region(name)
            self.regions.append(Region(name=name, profile=profile, state=state))
        self.step = 0
        self.global_emissions_history: list[dict] = []

    def advance(self) -> dict:
        """
        Run one 5-year period: one batch LLM call for all regions/agents,
        then compute emissions per region and aggregate globally.
        """
        region_states = [(r.name, r.state) for r in self.regions]
        all_outputs = run_batch_agents(region_states)
        for region in self.regions:
            region.step_from_outputs(all_outputs[region.name])

        raw_global = self._aggregate_global_emissions()
        step_idx = raw_global["step"]
        raw_sectors = {k: v for k, v in raw_global.items() if k not in ("step", "year")}
        blended_mt = blend_raw_with_empirical(raw_sectors, step_idx)
        display = ratio_to_1990_baseline(blended_mt)
        display["step"] = step_idx
        display["year"] = year_for_step(step_idx)
        self.global_emissions_history.append(display)
        self.step += 1
        self._evolve_state(blended_mt)
        return display

    def _aggregate_global_emissions(self) -> dict:
        """E_global_by_sector = sum over regions (approach.md Step 4)."""
        total = {sector: 0.0 for sector in EMISSION_SECTORS}
        for region in self.regions:
            d = region.emissions.to_dict()
            for sector in EMISSION_SECTORS:
                total[sector] += d.get(sector, 0.0)
        total["step"] = self.step
        total["year"] = year_for_step(self.step)
        return total

    def _evolve_state(self, global_emissions: dict) -> None:
        """Update region state for next step (bounded rates; placeholder for climate model)."""
        total_emissions = sum(
            global_emissions.get(k, 0.0) for k in EMISSION_SECTORS if isinstance(global_emissions.get(k), (int, float))
        )
        # Scale per-step damage: same calendar rate as the old 10-year step (0.02 * total per 10y → per 5y).
        scale = YEARS_PER_STEP / 10.0
        delta_damage = min(0.1, 0.02 * scale * (total_emissions or 0.1))
        for region in self.regions:
            d = region.state.get("climate_damage", 0.0)
            region.state["climate_damage"] = min(1.0, d + delta_damage)
