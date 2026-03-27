# Global Climate Agent Sim

Multi-agent LLM simulation of climate change and emissions across 7 regional blocs. Each region has 6 internal agents (Governance, Citizens, Industry, Energy, Land Use, International Relations) that update each **5-year** step; emissions are computed endogenously, calibrated to empirical **1990–2021** trends, and reported as **ratios to 1990** (blended Mt ÷ baseline Mt per sector).

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Add your OpenAI API key to `.env`:

   ```
   OPENAI_API_KEY=sk-...
   ```

## Run

```bash
python run_simulation.py --steps 7
```

Options:

- `--steps N`  Number of **5-year** periods (default: 7, roughly **1990–2020** on the calendar grid).
- `--output results.json`  Write global emissions ratios and metadata to a JSON file.

One LLM call is made per step (all 7 regions and 6 agents per region in a single prompt).

**Output metrics:** each sector value is **simulated blended MtCO2e ÷ 1990 baseline** for that sector (`BASE_MT_1990` in `simulation/emission_calibration.py`). **1.0** = 1990 level; values follow the empirical growth factors toward 2021, with a small agent-driven component.

## Plot results

After you have a JSON file (`results.json` from `--output` or any path), plot global emissions by sector:

```bash
python plot_results.py
```

This reads `results.json` in the current directory and writes **`emissions_by_period.png`** next to it, then opens an interactive chart window (matplotlib). The x-axis uses **`year`** when present (new format), or **`decade`** index for older result files.

To use a different file:

```bash
python plot_results.py path/to/your_results.json
```

Requires `matplotlib` (included in `requirements.txt`).

## Design

- **7 regions:** North America, Europe, Africa, South America, Southeast Asia, Asia Major, Australia.
- **6 agents per region:** Citizens → Industry → Energy → Land Use → International Relations → Governance (order fixed).
- **5-year timesteps.** Per step: each region reads state, updates agents, computes sector emissions; then global emissions are summed, blended with empirical Mt, and divided by 1990 baselines.
- **Emissions** are endogenous (from state and agent outputs). Sectors: energy_heat, transport, buildings, industry, deforestation, agriculture, carbon_removal.

See `approach.md` for full specification.
