"""
WorldSimulation: 7 regional blocs, one LLM call per timestep, global emissions aggregation.
"""

import math

from simulation.region import Region
from simulation.initial_state import REGIONAL_BLOCS, initial_state_for_region
from simulation.models import EMISSION_SECTORS
from simulation.agents.batch import run_batch_agents
from simulation.emission_calibration import (
    YEARS_PER_STEP,
    blend_raw_with_empirical,
    empirical_global_mt,
    ratio_to_1990_baseline,
    year_for_step,
)


class WorldSimulation:
    """
    Global coupled socio-climate simulation.
    One LLM call per timestep produces all region/agent outputs; then emissions are computed and aggregated.
    """

    def __init__(
        self,
        *,
        empirical_blend: float | None = None,
        scenario: str | None = None,
    ):
        """
        ``empirical_blend``: override weight in ``blend_raw_with_empirical`` (default: module ``EMPIRICAL_BLEND``).
        ``scenario``: optional ``climate-protection`` or ``growth-only`` — steers the batch LLM; use with lower blend.
        """
        self._empirical_blend = empirical_blend
        self._scenario = scenario
        self.regions: list[Region] = []
        for name in REGIONAL_BLOCS:
            profile = {"name": name}
            state = initial_state_for_region(name)
            self.regions.append(Region(name=name, profile=profile, state=state))
        self.step = 0
        self.global_emissions_history: list[dict] = []

    def advance(self) -> dict:
        """
        Run one calendar period (``YEARS_PER_STEP`` years): one batch LLM call for all regions/agents,
        then compute emissions per region and aggregate globally.
        """
        region_states = [(r.name, r.state) for r in self.regions]
        all_outputs = run_batch_agents(region_states, scenario=self._scenario)
        for region in self.regions:
            region.step_from_outputs(all_outputs[region.name])

        raw_global = self._aggregate_global_emissions()
        step_idx = raw_global["step"]
        raw_sectors = {k: v for k, v in raw_global.items() if k not in ("step", "year")}
        blended_mt = blend_raw_with_empirical(
            raw_sectors, step_idx, blend_weight=self._empirical_blend
        )
        # Step 0 is the 1990 baseline year: global totals must match BASE_MT_1990 so
        # ratio_to_1990_baseline is 1.0 for every sector. Blending with raw model mass
        # would break that; dynamics show from step 1 onward (first year after baseline).
        if step_idx == 0:
            blended_mt = empirical_global_mt(0)
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
        # NaN is truthy: (nan or 0.1) stays nan and poisons climate_damage → later prompts break.
        if not isinstance(total_emissions, (int, float)) or not math.isfinite(float(total_emissions)):
            total_emissions = 0.1
        elif total_emissions == 0.0:
            total_emissions = 0.1
        # Scale per-step damage: same calendar rate as the old 10-year step (0.02 * total per 10 calendar years).
        scale = YEARS_PER_STEP / 10.0
        delta_damage = min(0.1, 0.02 * scale * float(total_emissions))
        if not math.isfinite(delta_damage):
            delta_damage = 0.0
        for region in self.regions:
            d = float(region.state.get("climate_damage", 0.0))
            if not math.isfinite(d):
                d = 0.0
            region.state["climate_damage"] = min(1.0, d + delta_damage)
