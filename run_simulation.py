#!/usr/bin/env python3
"""
Run the global socio-climate simulation for a number of decades.
Usage: python run_simulation.py [--decades N]
"""

import argparse
import json
from simulation.world_simulation import WorldSimulation


def main():
    parser = argparse.ArgumentParser(description="Run multi-agent climate simulation")
    parser.add_argument("--decades", type=int, default=3, help="Number of 10-year steps to run")
    parser.add_argument("--output", type=str, default=None, help="Optional JSON file to write results")
    args = parser.parse_args()

    world = WorldSimulation()
    print(f"Running {args.decades} decade(s), {len(world.regions)} regions (1 LLM call per decade).\n")

    for _ in range(args.decades):
        global_emissions = world.step_decade()
        decade = global_emissions.get("decade", 0)
        print(f"--- Decade {decade} ---")
        for sector, value in global_emissions.items():
            if sector != "decade":
                print(f"  {sector}: {value:.4f}")
        net = sum(v for k, v in global_emissions.items() if k != "decade" and isinstance(v, (int, float)))
        print(f"  (net total: {net:.4f})\n")

    if args.output:
        out = {
            "decades_run": args.decades,
            "global_emissions_by_decade": world.global_emissions_history,
            "regions": [r.name for r in world.regions],
        }
        with open(args.output, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
