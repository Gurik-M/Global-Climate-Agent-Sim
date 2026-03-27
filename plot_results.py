#!/usr/bin/env python3
"""
Plot global emissions by sector from results.json (one line per sector over steps/years).
Usage: python plot_results.py [results.json]
"""

import json
import sys
import matplotlib.pyplot as plt


def _series_from_results(data: dict) -> tuple[list[dict], str, str]:
    """Return (list of step dicts, x_key, x_label)."""
    if "global_emissions_by_step" in data:
        return data["global_emissions_by_step"], "year", "Year"
    if "global_emissions_by_decade" in data:
        return data["global_emissions_by_decade"], "decade", "Decade index"
    return [], "", ""


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    with open(path) as f:
        data = json.load(f)

    steps_data, x_key, x_label = _series_from_results(data)
    if not steps_data:
        print("No step or decade data in", path)
        return

    xs = [d.get(x_key, d.get("step", i)) for i, d in enumerate(steps_data)]

    sector_keys = [
        k for k in steps_data[0]
        if k not in ("step", "year", "decade")
    ]

    plt.figure(figsize=(10, 6))
    for key in sector_keys:
        values = [d[key] for d in steps_data]
        plt.plot(xs, values, marker="o", label=key.replace("_", " ").title(), linewidth=2, markersize=6)

    plt.xlabel(x_label)
    plt.ylabel("Ratio to 1990 baseline (1.0 = same as 1990)")
    plt.title("Global emissions by sector (vs 1990 MtCO2e baselines)")
    plt.legend(loc="best", fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("emissions_by_period.png", dpi=150)
    print("Saved emissions_by_period.png")
    plt.show()


if __name__ == "__main__":
    main()
