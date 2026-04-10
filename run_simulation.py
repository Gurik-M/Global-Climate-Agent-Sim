#!/usr/bin/env python3
"""
Run the global socio-climate simulation for a number of multi-year steps.
Usage: python run_simulation.py [--steps N]
"""

import argparse
import json

from simulation.emission_calibration import (
    EMPIRICAL_BLEND,
    SCENARIO_EMPIRICAL_BLEND,
    YEARS_PER_STEP,
    default_simulation_step_count,
)
from simulation.world_simulation import WorldSimulation


def main():
    parser = argparse.ArgumentParser(description="Run multi-agent climate simulation")
    _default_steps = default_simulation_step_count()
    parser.add_argument(
        "--steps",
        type=int,
        default=_default_steps,
        help=(
            f"Number of periods to run (default: {_default_steps}, "
            f"{YEARS_PER_STEP:g}-year steps from 1990 through 2100)"
        ),
    )
    parser.add_argument("--output", type=str, default=None, help="Optional JSON file to write results")
    parser.add_argument(
        "--scenario",
        choices=["climate-protection", "growth-only"],
        default=None,
        help=(
            "Optional counterfactual: steers the batch LLM and sets empirical blend weight to "
            f"{SCENARIO_EMPIRICAL_BLEND} (default blend without this flag is {EMPIRICAL_BLEND})."
        ),
    )
    args = parser.parse_args()

    empirical_blend: float | None = None
    scenario: str | None = None
    if args.scenario is not None:
        empirical_blend = SCENARIO_EMPIRICAL_BLEND
        scenario = args.scenario

    world = WorldSimulation(empirical_blend=empirical_blend, scenario=scenario)
    print(
        f"Running {args.steps} step(s) of {YEARS_PER_STEP:g} years each, {len(world.regions)} regions "
        "(1 LLM call per step).\n"
    )

    for _ in range(args.steps):
        global_emissions = world.advance()
        step = global_emissions.get("step", 0)
        year = global_emissions.get("year", 0)
        print(f"--- Step {step} (year {year:.0f}) ---")
        for key, value in global_emissions.items():
            if key not in ("step", "year"):
                print(f"  {key}: {value:.4f}")
        print()

    if args.output:
        blend_used = SCENARIO_EMPIRICAL_BLEND if args.scenario else EMPIRICAL_BLEND
        out = {
            "years_per_step": YEARS_PER_STEP,
            "steps_run": args.steps,
            "scenario": args.scenario,
            "empirical_blend": blend_used,
            "global_emissions_by_step": world.global_emissions_history,
            "regions": [r.name for r in world.regions],
        }
        with open(args.output, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
