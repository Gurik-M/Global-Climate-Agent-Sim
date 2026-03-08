# Global Climate Agent Sim

Multi-agent LLM simulation of climate change and emissions across 7 regional blocs. Each region has 6 internal agents (Governance, Citizens, Industry, Energy, Land Use, International Relations) that update each decade; emissions are computed endogenously and aggregated globally.

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
python run_simulation.py --decades 3
```

Options:

- `--decades N`  Number of 10-year steps (default: 3).
- `--output results.json`  Write global emissions and metadata to a JSON file.

One LLM call is made per decade (all 7 regions and 6 agents per region in a single prompt).

## Design

- **7 regions:** North America, Europe, Africa, South America, Southeast Asia, Asia Major, Australia.
- **6 agents per region:** Citizens → Industry → Energy → Land Use → International Relations → Governance (order fixed).
- **10-year timesteps.** Per decade: each region reads state, updates agents, computes sector emissions; then global emissions are summed.
- **Emissions** are endogenous (from state and agent outputs). Sectors: energy_heat, transport, buildings, industry, deforestation, agriculture, carbon_removal.

See `approach.md` for full specification.
