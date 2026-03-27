"""
Region: one of 7 regional blocs with state, emissions, and policy.
Agent outputs are applied via step_from_outputs (from one batch LLM call per 5-year step).
"""

from simulation.models import PolicyPackage, EmissionsProfile
from simulation.emissions import compute_emissions


class Region:
    """
    One regional bloc with static profile, dynamic state,
    and sector-level emissions (approach.md §2).
    """

    def __init__(self, name: str, profile: dict, state: dict):
        self.name = name
        self.profile = profile
        self.state = dict(state)
        self.emissions = EmissionsProfile()
        self.policy_package: PolicyPackage | None = None

    def step_from_outputs(self, outputs: dict) -> None:
        """
        Apply agent outputs from the batch LLM call and compute emissions.
        Outputs must have keys: citizens, industry, energy, land_use, international, governance.
        """
        policy = PolicyPackage.from_dict(outputs["governance"])
        self.policy_package = policy
        self._compute_emissions(
            self.state,
            policy,
            outputs["citizens"],
            outputs["industry"],
            outputs["energy"],
            outputs["land_use"],
        )

    def _compute_emissions(
        self,
        state: dict,
        policy: PolicyPackage,
        citizens: dict,
        industry: dict,
        energy: dict,
        land_use: dict,
    ) -> None:
        region_scale = self._emissions_scale()
        self.emissions = compute_emissions(
            state=state,
            policy=policy,
            citizens=citizens,
            industry=industry,
            energy=energy,
            land_use=land_use,
            region_scale=region_scale,
        )

    def _emissions_scale(self) -> float:
        """Scale emissions by region size (population and GDP proxy)."""
        pop = self.state.get("population", 1.0)
        gdp = self.state.get("gdp", 1.0)
        return 0.1 * (pop ** 0.5) * (gdp ** 0.3)
