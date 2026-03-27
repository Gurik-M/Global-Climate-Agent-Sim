#!/usr/bin/env python3
"""
Run the global socio-climate simulation for a number of 5-year steps.
Usage: python run_simulation.py [--steps N]
"""

import argparse
import json
from simulation.world_simulation import WorldSimulation


def main():
    parser = argparse.ArgumentParser(description="Run multi-agent climate simulation")
    parser.add_argument(
        "--steps",
        type=int,
        default=7,
        help="Number of 5-year periods to run (default: 7, ~1990–2020 on the calendar grid)",
    )
    parser.add_argument("--output", type=str, default=None, help="Optional JSON file to write results")
    args = parser.parse_args()

    world = WorldSimulation()
    print(
        f"Running {args.steps} step(s) of 5 years each, {len(world.regions)} regions "
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
        out = {
            "years_per_step": 5,
            "steps_run": args.steps,
            "global_emissions_by_step": world.global_emissions_history,
            "regions": [r.name for r in world.regions],
        }
        with open(args.output, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
