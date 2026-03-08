# approach.md

## Project Overview

Build a **global coupled socio-climate simulation** with:

- **7 regional blocs**
- **6 internal agents per bloc**
- **10-year timesteps**
- **endogenous emissions generation** by region and sector
- **global emissions aggregation**
- later coupling to a climate model that feeds damages back into each region

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

Each timestep is **10 years**.

At each timestep, every region:
1. reads its current state
2. updates all internal agents
3. computes emissions by sector
4. contributes to global emissions

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
- choose policy package for the decade
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

The simulation uses **10-year timesteps**.

Interpretation:
- each timestep = one decade
- state variables are updated once per decade
- policy changes represent decade-level directional shifts
- emissions outputs are decade-level emissions totals or average annualized emissions within that decade

Important implementation note:
- even though the timestep is 10 years, the state should still be smooth and continuous enough that transitions are not unrealistically abrupt
- use bounded rates of change so variables do not jump too sharply in one timestep unless caused by a shock

---

## Required Simulation Loop

The simulation must follow this exact loop.

# For each decade:

## Step 1: each region reads current state

Each region reads:
- economy
- population
- quality of life
- climate damages from previous year
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

These emissions must be derived from:
- regional state
- current agent outputs
- previous timestep conditions
- policy package chosen by governance

Do **not** hardcode emissions paths externally.

Emissions must be endogenous to agent behavior.

---

## Step 4: aggregate to global emissions

Aggregate all regional emissions into global emissions.

Formula:

E_global = sum(E_agents)

And calculate and output E_global_by_sector = {
    "energy_heat": sum(region.emissions["energy_heat"] for region in regions),
    "transport": sum(region.emissions["transport"] for region in regions),
    "buildings": sum(region.emissions["buildings"] for region in regions),
    "industry": sum(region.emissions["industry"] for region in regions),
    "deforestation": sum(region.emissions["deforestation"] for region in regions),
    "agriculture": sum(region.emissions["agriculture"] for region in regions),
    "carbon_removal": sum(region.emissions["carbon_removal"] for region in regions),
}

# Implementation Requirements

## 1. Use a modular object-oriented design

Recommended top-level classes:

* `WorldSimulation`
* `Region`
* `GovernanceAgent`
* `CitizensAgent`
* `IndustryAgent`
* `EnergyAgent`
* `LandUseAgent`
* `InternationalRelationsAgent`

Optional support classes:

* `RegionState`
* `PolicyPackage`
* `EmissionsProfile`
* `ClimateDamageProfile`

---

## 2. Region object structure

Each `Region` should contain:

* static regional profile
* dynamic state variables
* all 6 internal agents
* emissions outputs by sector
* policy package for current timestep

Recommended structure:

```python
class Region:
    name: str
    profile: dict
    state: dict
    governance: GovernanceAgent
    citizens: CitizensAgent
    industry: IndustryAgent
    energy: EnergyAgent
    land_use: LandUseAgent
    international: InternationalRelationsAgent
    emissions: dict
    policy_package: dict
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
* climate damages from previous timestep
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

Use interpretable equations, not black-box predictions.

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
3. Do not make emissions exogenous.
4. Do not collapse all behavior into one region-level scalar.
5. Preserve the exact 6 agents per region.
6. Preserve the exact 7 regional blocs.
7. Preserve the exact simulation loop and order of updates.
8. Use decade timesteps.
9. Make it easy to later attach a climate damage model.
10. Prefer clean, extensible Python over premature optimization.
