#!/usr/bin/env python3
"""
Plot global emissions by sector from results.json (one line per sector over decades).
Usage: python plot_results.py [results.json]
"""

import json
import sys
import matplotlib.pyplot as plt


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    with open(path) as f:
        data = json.load(f)

    decades_data = data["global_emissions_by_decade"]
    if not decades_data:
        print("No decade data in", path)
        return

    # X = decade indices
    decades = [d["decade"] for d in decades_data]

    # One line per outcome (exclude "decade" key)
    sector_keys = [k for k in decades_data[0] if k != "decade"]

    plt.figure(figsize=(10, 6))
    for key in sector_keys:
        values = [d[key] for d in decades_data]
        plt.plot(decades, values, marker="o", label=key.replace("_", " ").title(), linewidth=2, markersize=6)

    plt.xlabel("Decade")
    plt.ylabel("Global emissions (arbitrary units)")
    plt.title("Global emissions by sector over decades")
    plt.legend(loc="best", fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("emissions_by_decade.png", dpi=150)
    print("Saved emissions_by_decade.png")
    plt.show()


if __name__ == "__main__":
    main()
