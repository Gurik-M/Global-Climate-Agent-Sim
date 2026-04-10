# approach.md

## Project Overview

Build a **global coupled socio-climate simulation** with:

- **7 regional blocs**
- **6 internal agents per bloc**
- **5-year timesteps**
- **endogenous emissions generation** by region and sector (interpretable formulas from state and agent outputs)
- **global emissions aggregation**, then **empirical calibration** to real **1990–2021** sector trends (MtCO2e), and **ratio-based** global reporting (**current Mt ÷ 1990 baseline** per sector, so **1.0** = 1990 level)
- **climate damage** updated each 5-year step from calibrated global totals (placeholder for a fuller climate model)

The goal is to replace fixed human emissions assumptions with a structured simulation in which emissions emerge from political, social, industrial, energy, land-use, and international dynamics.

---

## High-Level Model Design

The world is modeled as **7 regional blocs**:

- North America
- Europe
- Africa
- South America
- Southeast Asia
- Asia Major
- Australia

Each regional bloc contains **6 internal agents**:

1. Governance
2. Citizens
3. Industry
4. Energy
5. Land Use
6. International Relations

Each timestep is **5 years**.

At each timestep, every region:
1. reads its current state
2. updates all internal agents (one batched LLM call covers all regions for that step)
3. computes emissions by sector
4. contributes to global emissions (then globals are summed, blended with empirical MtCO2e, and exported as **ratios ÷ 1990**)

---

## Core Design Principle

Do **not** model individual people or countries.

Each region is a **macro-social system** represented by competing internal agents that stand in for major political, economic, and behavioral forces.

This means:
- the region is the main simulation unit
- the 6 internal agents generate regional decisions and emissions
- the output of each region is sector-level emissions
- all regional emissions are aggregated into global emissions

---

## Regional Blocs

### 1. North America
Characteristics:
- high GDP/capita
- high transport/building demand
- strong industrial and fossil legacy
- moderate/high public influence on policy
- high innovation capacity
- mixed political polarization

### 2. Europe
Characteristics:
- high climate policy responsiveness
- high regulatory capacity
- high international norm sensitivity
- lower population growth
- relatively advanced energy transition

### 3. Africa
Characteristics:
- low GDP/capita on average
- high development priority
- lower historical emissions
- high climate vulnerability
- lower institutional capacity on average
- energy access central

### 4. South America
Characteristics:
- medium development
- strong land-use and deforestation relevance
- agricultural importance
- moderate climate vulnerability
- mixed governance capacity

### 5. Southeast Asia
Characteristics:
- high growth pressure
- urbanization
- coastal vulnerability
- manufacturing expansion
- energy demand growth

### 6. Asia Major
Characteristics:
- very large population and industrial base
- huge energy demand
- strong manufacturing importance
- mixed state capacity and governance styles
- major leverage over global emissions

### 7. Australia
Characteristics:
- smaller population
- high GDP/capita
- fossil export relevance
- strong climate exposure in wildfire/heat
- relatively high institutional capacity

---

## Internal Agents Per Region

Each region has the following exact 6 agents.

### 1. Governance Agent
Represents overall regional policy direction.

Responsibilities:
- choose policy package for the 5-year step
- balance public pressure, economic growth, lobbying, climate damages, and diplomatic pressure
- influence all major emitting sectors

Outputs:
- climate policy strength
- fossil policy stance
- industrial regulation level
- efficiency/infrastructure policy
- land-use enforcement
- agriculture incentives
- carbon removal investment
- international climate cooperation posture

---

### 2. Citizens Agent
Represents households, consumers, and public opinion.

Responsibilities:
- update public pressure based on quality of life, climate damages, and economic tradeoffs
- influence governance responsiveness
- affect transport, building, and consumption demand

Outputs:
- public pressure for climate action
- transition tolerance
- cost sensitivity
- social demand for adaptation vs mitigation

---

### 3. Industry Agent
Represents manufacturing, firms, and industrial incumbents.

Responsibilities:
- update transition stance
- update lobbying pressure
- decide degree of industrial decarbonization vs fossil lock-in
- affect manufacturing & industry emissions

Outputs:
- lobbying strength
- clean investment level
- industrial emissions intensity
- resistance to regulation

---

### 4. Energy Agent
Represents the energy supply system.

Responsibilities:
- update electricity and fuel supply plans
- determine fossil vs low-carbon mix
- respond to governance policy and energy demand growth
- affect energy & heat, buildings, and transport electrification potential

Outputs:
- energy mix
- grid decarbonization pace
- fossil lock-in level
- electrification support capacity

---

### 5. Land Use Agent
Represents agriculture, forests, land conversion, and food system pressure.

Responsibilities:
- update land pressure
- determine deforestation and agricultural emissions trajectory
- respond to food demand, enforcement, and climate stress

Outputs:
- deforestation rate
- agricultural emissions intensity
- reforestation/conservation level
- land-use transition pressure

---

### 6. International Relations Agent
Represents diplomacy, cooperation, peer effects, and trade pressure.

Responsibilities:
- update cooperation stance
- respond to other regional blocs
- influence governance via international norms and trade/diplomatic pressure

Outputs:
- climate cooperation level
- norm sensitivity
- trade/diplomatic pressure received and exerted
- reputation effects

---

## Time Resolution

The simulation uses **5-year timesteps**.

Interpretation:
- each timestep = five calendar years
- state variables are updated once per step
- policy changes represent step-level directional shifts
- emissions outputs are associated with the **calendar year at the start** of each step

Important implementation note:
- even though the timestep is 5 years, the state should still be smooth enough that transitions are not unrealistically abrupt
- use bounded rates of change so variables do not jump too sharply in one timestep unless caused by a shock

**Calendar mapping:** simulation step index `s` maps to calendar year **Y = 1990 + 5·s** (step start). Empirical trends are anchored to **1990** and **2021**; between those years growth is **linear in time**; after 2021 the **same linear slope continues** (extrapolation). Five-year steps sample the 1990–2021 trend more finely than 10-year steps.

---

## Empirical calibration and ratio outputs

Global reporting is calibrated so sector **trajectories** align with real-world **global** greenhouse-gas inventory style data: **MtCO2e**, **1990 baselines**, and **multiplicative change from 1990 to 2021** per sector (from empirical charts; industrial processes, electricity/heat, transport, manufacturing/construction, agriculture, LULUCF, etc.). **Exported values** are **dimensionless ratios**: **blended Mt / 1990 baseline Mt** for each sector (same idea as **GROWTH_1990_TO_2021** over time: **1.0** = 1990 level, **1.88** ≈ +88% for electricity/heat at 2021).

### 1990 global baselines (MtCO2e)

These are the targets at **Y = 1990** (`BASE_MT_1990` in code):

| Sector (model key) | MtCO2e (1990) | Notes |
|--------------------|---------------|--------|
| `energy_heat` | 8,653 | Electricity / heat (user-provided) |
| `transport` | 4,734 | Transportation (user-provided) |
| `buildings` | 4,000 | **Proxy:** manufacturing & construction level from charts (~4,000 Mt in 1990); the model’s “buildings” sector is aligned to that inventory line |
| `industry` | 1,004 | Industrial processes (user-provided) |
| `deforestation` | 2,027 | Land use, deforestation, LULUCF source side (user-provided) |
| `agriculture` | 4,976 | Agriculture (user-provided) |

### Growth factors (1990 → 2021)

Each positive sector has a multiplicative factor **G** at **2021** relative to **1990** (`GROWTH_1990_TO_2021`). Linear interpolation in time:

- Let **t = (Y − 1990) / (2021 − 1990)**.
- Sector factor **F(Y) = 1 + (G − 1)·t** (for **Y** outside [1990, 2021], **t** is not clamped—the line extends).

Empirical **G** values used:

| Sector | G (2021 vs 1990) | Interpretation (approx.) |
|--------|------------------|---------------------------|
| `energy_heat` | 1.88 | +88% |
| `transport` | 1.66 | +66% |
| `buildings` | 1.60 | +60% (manufacturing/construction trend) |
| `industry` | 3.25 | +225% |
| `deforestation` | 0.66 | −34% (LULUCF / land-use trend) |
| `agriculture` | 1.18 | +18% |

**Empirical global Mt for a positive sector:**

**E_emp(s, Y) = BASE_MT_1990[s] · F_s(Y)**.

### Carbon removal (negative emissions)

Inventory-style **removal** is not split the same way in the charts; the model uses a **gross removal magnitude** (MtCO2e) that increases from 1990 to 2021, then continues on the same line:

- **REMOVAL_MAGNITUDE_MT_1990 = 300**
- **REMOVAL_MAGNITUDE_MT_2021 = 450**

**E_emp(carbon_removal, Y) = −magnitude(Y)** (negative = removal).

Tunable in `emission_calibration.py` if better priors are available.

### Blending raw simulation with empirical targets

Let **E_raw** be the vector of **raw** global sums from the regions (same sector keys). Let **E_target** be **E_emp** at the step’s calendar year **Y**.

1. **Positive sectors:** scale **E_raw** so the sum of positive components matches **sum(E_target positive)**. Call the scaled vector **E_scaled**.
2. **Blend:** **E_blend = w · E_target + (1 − w) · E_scaled**, with **w = EMPIRICAL_BLEND** (default **0.88**). So **~88%** empirical trajectory, **~12%** scaled agent-driven shape.
3. **carbon_removal:** same **w** between **E_target[carbon_removal]** and **E_raw[carbon_removal]**.

If raw positive mass is zero, the blend falls back to **E_target** for positive sectors.

### Scenario mode (`--scenario` CLI flag)

The CLI can pass **`--scenario climate-protection`** or **`--scenario growth-only`**. When either is set:

1. **Blend weight:** **w** is set to **`SCENARIO_EMPIRICAL_BLEND = 0.4`** instead of **`EMPIRICAL_BLEND = 0.88`**. The same formula **E_blend = w · E_target + (1 − w) · E_scaled** applies; the **(1 − w)** term is **60%**, so the **scaled raw** global vector from the simulation has a much larger share of the blended result than in the default run. Reported global ratios still use **E_blend ÷ 1990 baseline** per sector, but the path is **less tightly tied** to the empirical **MtCO2e** trajectory and **more sensitive** to agent outputs and regional formulas.

2. **LLM steering:** `simulation/agents/batch.py` appends a short **scenario paragraph** to the system prompt so the model biases all regions’ **0–1** agent fields in a consistent direction:
   - **`climate-protection`:** favor stronger mitigation and adaptation signals (e.g. higher climate policy ambition, lower fossil lock-in, conservation and electrification where consistent with state).
   - **`growth-only`:** favor economic and industrial expansion (e.g. higher demand and industrial intensity where plausible; climate policy secondary to development).

When **`--scenario` is omitted**, behavior matches the **default**: **w = 0.88** and **no** scenario paragraph. Regional emissions formulas and the batch JSON schema are unchanged; only **w** and the **optional** prompt suffix differ.

### Ratio to 1990 baseline (exported metrics)

Let **B(s)** be **BASE_MT_1990[s]** for positive sectors, and **B(carbon_removal) = BASELINE_CARBON_REMOVAL_MT_1990** (e.g. **−300** MtCO2e).

- For each sector **s**: **output(s) = E_blend(s) / B(s)**.
- **carbon_removal:** **output = E_blend(carbon_removal) / B(carbon_removal)** (both negative → ratio **> 0** when removal magnitude grows).

So **1.0** means “same as 1990” for that sector; trends follow the empirical **GROWTH_1990_TO_2021** shape over calendar time (plus agent noise via **1 − w**).

### JSON output shape (`run_simulation.py`)

The top-level JSON file includes:

- **`years_per_step`**: `5`
- **`steps_run`**: number of periods simulated
- **`scenario`**: `null`, **`"climate-protection"`**, or **`"growth-only"`** — mirrors the CLI `--scenario` flag (omitted or `null` when the default run was used)
- **`empirical_blend`**: **`0.88`** (default) or **`0.4`** when `--scenario` was passed — the **w** used in blending for that run
- **`global_emissions_by_step`**: list of objects, one per step, each with:
  - **`step`**: integer index `s` (0, 1, 2, …)
  - **`year`**: calendar start year **1990 + 5·s**
  - **Sector keys** (`energy_heat`, `transport`, `buildings`, `industry`, `deforestation`, `agriculture`, `carbon_removal`): **ratio = blended Mt ÷ 1990 baseline** for that sector (see tables above)

Older result files may use **`global_emissions_by_decade`** and **`decade`**; plotting code can accept both.

### Code references

- Constants **`BASE_MT_1990`**, **`GROWTH_1990_TO_2021`**, **`EMPIRICAL_BLEND`**, **`SCENARIO_EMPIRICAL_BLEND`**, **`YEARS_PER_STEP`**, removal magnitudes: **`simulation/emission_calibration.py`**
- **Blend** then **ratio**: `blend_raw_with_empirical` (optional **`blend_weight`**) → `ratio_to_1990_baseline`
- Main loop: **`WorldSimulation.advance()`** (increments **`step`** after each 5-year period); **`WorldSimulation`** accepts optional **`empirical_blend`** and **`scenario`** for scenario runs

### What stays endogenous

- **Per-region** emissions formulas and **LLM-produced** agent outputs still determine **raw** global sums and how they **deviate** within the **(1 − w)** term.
- **Reported** globals and trends are **calibrated**; they are not a pure unconstrained sum of arbitrary units.

---

## LLM batch (implementation)

In this repository, **Step 2** is implemented as **one** OpenAI chat completion per **5-year step** (`simulation/agents/batch.py`): the model returns JSON for all seven regions, each with **`citizens`**, **`industry`**, **`energy`**, **`land_use`**, **`international`**, **`governance`** objects (numeric fields clamped to **[0, 1]**). There is **not** a separate Python class per agent type; agent behavior is defined via prompt fragments (`simulation/agents/*.py`) composed into a single system prompt. When **`run_simulation.py`** is invoked with **`--scenario`**, the **same** schema and clamping apply; **`batch.py`** only appends a **scenario instruction block** to the system prompt (see § **Scenario mode** under empirical calibration).

---

## Required Simulation Loop

The simulation must follow this exact loop.

# For each 5-year step:

## Step 1: each region reads current state

Each region reads:
- economy
- population
- quality of life
- climate damages from the previous step
- trade/diplomatic influence from other regions

This state is the shared context for all 6 internal agents.

---

## Step 2: internal agent updates

Within each region, update the 6 internal agents in this order:

1. citizens update public pressure
2. industry updates transition/lobbying stance
3. energy sector updates supply plans
4. agriculture/land-use updates land pressure
5. international relations agent updates cooperation stance
6. governance agent chooses policy package

Important:
- governance acts **after** reading the other agents’ updated signals
- governance should use the outputs of the other 5 agents as inputs into policy choice

**Implementation:** one batched LLM call produces all six output bundles for all regions for that step (`run_batch_agents`). Conceptual order above is reflected in the prompt design (governance chosen in light of the other five).

---

## Step 3: compute emissions by sector

For each region, compute emissions for:

- energy & heat
- transportation
- buildings
- manufacturing & industry
- deforestation
- agriculture
- carbon removal

These **regional** sector totals are derived from:

- regional state
- current agent outputs (from the batch LLM response)
- policy package chosen by governance

Implementation (`simulation/emissions.py`): interpretable formulas map state, policy, and agent outputs into an `EmissionsProfile` per region. Values are in **arbitrary model units** before global calibration. Regional scaling uses population and GDP proxies (`Region._emissions_scale`).

Emissions at this stage are **endogenous** to agent outputs and state.

---

## Step 4: aggregate to global emissions and calibrate

### 4a. Raw global aggregation

Sum over all regions:

**E_raw_global[sector] = Σ_region region.emissions[sector]**

Same sector keys as above (`simulation/models.py`: `EMISSION_SECTORS`). In code, the aggregated dict also carries **`step`** and **`year`** for bookkeeping before blending.

### 4b. Empirical calibration (trend-aligned global totals)

Raw globals are **blended** with **empirical MtCO2e-style targets** so that **reported global trajectories** match observed 1990–2021 sector trends (see **§ Empirical calibration and ratio outputs**). Constants and formulas live in `simulation/emission_calibration.py`.

This does **not** replace regional physics: agents still drive **raw** regional emissions; the blend sets how strongly **global** reporting follows historical curves.

### 4c. Ratio output (e.g. `results.json`)

The simulation **records** and returns **ratios to 1990** for each sector:

- **Positive sectors:** **blended Mt ÷ BASE_MT_1990[sector]** (dimensionless; **1.0** = 1990 level).
- **carbon_removal:** **blended Mt ÷ BASELINE_CARBON_REMOVAL_MT_1990** (typically negative ÷ negative → positive ratio when sinks strengthen).

### 4d. Climate damage update

`WorldSimulation._evolve_state` uses the **blended MtCO2e-style global dict** (after blend, before ratio conversion) to update each region’s `climate_damage`. Per-step damage is scaled by **(5/10)** relative to the old 10-year step so the **calendar** rate of change is comparable.

# Implementation Requirements

## 1. Modular design (this repository)

Top-level types in code:

* `WorldSimulation` — 5-year step loop via **`advance()`**, raw global aggregation, blend, **ratio-to-1990** export, history list, climate damage
* `Region` — state, policy package, `EmissionsProfile`, `step_from_outputs`

Supporting structures (`simulation/models.py`):

* `PolicyPackage` (governance outputs)
* `EmissionsProfile` (sector emissions)
* Typed region state schema

Agent outputs are **not** separate Python classes; they are **dicts** keyed by agent name, filled by the batch LLM. Prompt modules under `simulation/agents/` define each agent’s **JSON keys** and **prompt fragments**.

---

## 2. Region object structure

Each `Region` contains:

* static regional profile (`name`, `profile`)
* dynamic state variables (`state`)
* emissions outputs by sector (`emissions: EmissionsProfile`)
* policy package for current timestep (`policy_package: PolicyPackage`)

Agent outputs are **not** stored as sub-objects; they are passed into `step_from_outputs` only for the computation step.

```python
class Region:
    name: str
    profile: dict
    state: dict
    emissions: EmissionsProfile
    policy_package: PolicyPackage | None
```

---

## 3. Required region state variables

Each region should at minimum track:

* population
* GDP
* GDP per capita
* quality of life
* political stability
* political polarization
* climate vulnerability
* international perception
* public-to-policy responsiveness
* innovation capacity
* fossil legacy / carbon lock-in
* industrial intensity
* energy demand level
* transport demand level
* building demand level
* land-use pressure
* agriculture intensity
* climate damages from the previous 5-year step
* trade/diplomatic influence score

You may add more variables if useful, but keep the model interpretable.

---

## 4. Suggested state schema

Use something like this:

```python
region.state = {
    "population": float,
    "gdp": float,
    "gdp_per_capita": float,
    "quality_of_life": float,
    "political_stability": float,
    "political_polarization": float,
    "international_perception": float,
    "public_policy_responsiveness": float,
    "innovation_capacity": float,
    "fossil_legacy": float,
    "industrial_intensity": float,
    "energy_demand": float,
    "transport_demand": float,
    "building_demand": float,
    "land_use_pressure": float,
    "agriculture_intensity": float,
    "climate_damage": float,
    "trade_diplomatic_influence": float,
}
```

---

## 5. Emissions logic expectations

Use interpretable equations, not black-box predictions. Per-region values are in **arbitrary units** until the **global** blend; **reported** globals are **MtCO2e-aligned** after calibration and **ratio-normalized** (÷ 1990 baseline) for export.

### Energy & Heat

Depends on:

* energy demand
* fossil share
* clean energy share
* climate ambition
* fossil restriction level

### Transportation

Depends on:

* transport demand
* electrification support
* urbanization proxy
* public transition tolerance
* transport policy support

### Buildings

Depends on:

* building demand
* efficiency policy
* energy mix
* quality of life
* electrification support

### Manufacturing & Industry

Depends on:

* industrial intensity
* industrial emissions intensity
* industrial regulation
* innovation capacity
* lobbying/policy interaction

### Deforestation

Depends on:

* land pressure
* land-use enforcement
* development pressure
* reforestation effort

### Agriculture

Depends on:

* agriculture intensity
* climate damage
* agricultural reform support
* land-use pressure

### Carbon Removal

Depends on:

* governance investment
* innovation capacity
* institutional capacity

---

## 6. Regional initialization

Initialize each region using profile-specific priors.

### North America

Set higher initial values for:

* GDP per capita
* transport demand
* building demand
* fossil legacy
* innovation capacity
* public-policy responsiveness

Set moderate/high values for:

* polarization
* industrial intensity

### Europe

Set higher initial values for:

* climate ambition
* regulatory capacity
* international norm alignment
* clean energy share

Set lower values for:

* population growth
* fossil lock-in relative to North America / Asia Major

### Africa

Set higher initial values for:

* development pressure
* climate vulnerability
* energy access need

Set lower initial values for:

* GDP per capita
* institutional capacity
* historical emissions contribution

### South America

Set higher initial values for:

* land-use pressure
* deforestation relevance
* agricultural significance

Set medium values for:

* development level
* governance capacity
* climate vulnerability

### Southeast Asia

Set higher initial values for:

* growth pressure
* urbanization
* manufacturing expansion
* energy demand growth
* coastal vulnerability

### Asia Major

Set higher initial values for:

* population
* industrial intensity
* energy demand
* manufacturing importance
* leverage over global emissions

Set mixed values for:

* governance capacity
* policy responsiveness

### Australia

Set higher initial values for:

* GDP per capita
* institutional capacity
* fossil export relevance
* wildfire/heat exposure

Set lower values for:

* population

---

## 7. Important constraints

1. Keep the model interpretable.
2. Use structured state variables and equations.
3. **Regional** emissions remain **endogenous** (state + agent outputs + formulas). **Globally reported** outputs are **calibrated** to empirical MtCO2e trends, then **divided by 1990 baselines** for export (see § Empirical calibration and ratio outputs); tune **`EMPIRICAL_BLEND`** toward `0` for a more purely model-driven global path, or use **`--scenario`** so **`w = SCENARIO_EMPIRICAL_BLEND`** (0.4) plus optional LLM steering.
4. Do not collapse all behavior into one region-level scalar.
5. Preserve the exact 6 agents per region.
6. Preserve the exact 7 regional blocs.
7. Preserve the exact simulation loop and order of updates (conceptually; batch LLM implements it in one call).
8. Use **5-year** timesteps.
9. Climate damage is updated each step from **blended** global emissions (`_evolve_state`); a fuller climate model can replace or extend this.
10. Prefer clean, extensible Python over premature optimization.

### Key files

| File | Role |
|------|------|
| `simulation/emissions.py` | Per-region sector formulas |
| `simulation/emission_calibration.py` | `BASE_MT_1990`, `GROWTH_1990_TO_2021`, `EMPIRICAL_BLEND`, `SCENARIO_EMPIRICAL_BLEND`, `YEARS_PER_STEP`, blend, `ratio_to_1990_baseline` |
| `simulation/world_simulation.py` | `WorldSimulation.advance()` — loop, raw sum, blend, ratios, history, `_evolve_state`; optional scenario kwargs |
| `simulation/agents/batch.py` | One LLM call per 5-year step, JSON for all regions; optional `scenario` prompt suffix |
| `run_simulation.py` | CLI: `--steps N` (default 7 ≈ 1990–2020), `--output` JSON, `--scenario` |
| `plot_results.py` | Plots ratios vs `year` or legacy `decade`; writes `emissions_by_period.png` |
