"""
Calibrate global sector totals to empirical GHG trends (MtCO2e, 1990 baseline, 1990–2021 shape).

Sources aligned with user-provided 1990 levels and IPCC-style global sector charts
(industrial processes, electricity/heat, transport, agriculture, LULUCF; manufacturing/
construction used as proxy for the buildings sector in this model).

Normalization for results.json:
  Each sector value is (blended simulated Mt) / (1990 baseline for that sector).
  Positive sectors use BASE_MT_1990; carbon_removal uses BASELINE_CARBON_REMOVAL_MT_1990 (-300 Mt).
  So 1.0 means "same as 1990"; values track multiplicative change like GROWTH_1990_TO_2021 over time.
"""

from __future__ import annotations

from simulation.models import EMISSION_SECTORS

# --- 1990 global baselines (MtCO2e) ------------------------------------------
# User-provided: industrial, energy_heat, transport, agriculture, land-use/deforestation.
# Buildings: manufacturing & construction ~4,000 Mt in 1990 (chart); used as proxy.

BASE_MT_1990: dict[str, float] = {
    "energy_heat": 8653.0,
    "transport": 4734.0,
    "buildings": 4000.0,
    "industry": 1004.0,
    "deforestation": 2027.0,
    "agriculture": 4976.0,
}

# Multiplicative change 1990 → 2021 (31 years) from empirical trend charts.
GROWTH_1990_TO_2021: dict[str, float] = {
    "energy_heat": 1.88,
    "transport": 1.66,
    "buildings": 1.60,
    "industry": 3.25,
    "deforestation": 0.66,
    "agriculture": 1.18,
}

# Gross carbon removal / sinks (MtCO2e); model stores removal as negative emissions.
REMOVAL_MAGNITUDE_MT_1990 = 300.0
REMOVAL_MAGNITUDE_MT_2021 = 450.0

# 1990 removal in MtCO2e (negative). Used as ratio denominator for carbon_removal output.
BASELINE_CARBON_REMOVAL_MT_1990 = -REMOVAL_MAGNITUDE_MT_1990

YEAR_START = 1990.0
YEAR_END_TREND = 2021.0

# Simulation advances in 5-year periods (clearer sampling between 1990 and 2021).
YEARS_PER_STEP = 5

# Weight of empirical target vs scaled raw model (preserves agent-driven spread).
EMPIRICAL_BLEND = 0.88


def year_for_step(step_index: int, start_year: float = YEAR_START) -> float:
    """Calendar year at the start of this simulation step (step 0 = 1990)."""
    return start_year + float(YEARS_PER_STEP) * step_index


def _linear_growth_factor(year: float, growth_at_end: float) -> float:
    """Factor 1.0 at YEAR_START, growth_at_end at YEAR_END_TREND; linear beyond."""
    span = YEAR_END_TREND - YEAR_START
    t = (year - YEAR_START) / span if span > 0 else 0.0
    return 1.0 + (growth_at_end - 1.0) * t


def empirical_sector_mt_positive(sector: str, year: float) -> float:
    if sector not in BASE_MT_1990:
        return 0.0
    g = GROWTH_1990_TO_2021.get(sector, 1.0)
    return BASE_MT_1990[sector] * _linear_growth_factor(year, g)


def empirical_carbon_removal_mt(year: float) -> float:
    """Negative MtCO2e (removal). Magnitude grows ~1990→2021 then continues same slope."""
    span = YEAR_END_TREND - YEAR_START
    t = (year - YEAR_START) / span if span > 0 else 0.0
    mag = REMOVAL_MAGNITUDE_MT_1990 + t * (REMOVAL_MAGNITUDE_MT_2021 - REMOVAL_MAGNITUDE_MT_1990)
    return -mag


def empirical_global_mt(step_index: int) -> dict[str, float]:
    """Target global sector totals in MtCO2e for this step (year at step start)."""
    y = year_for_step(step_index)
    out: dict[str, float] = {}
    for s in EMISSION_SECTORS:
        if s == "carbon_removal":
            out[s] = empirical_carbon_removal_mt(y)
        else:
            out[s] = empirical_sector_mt_positive(s, y)
    return out


def blend_raw_with_empirical(raw: dict[str, float], step_index: int) -> dict[str, float]:
    """
    Blend empirical Mt targets with region-aggregated raw emissions (same keys as EMISSION_SECTORS).
    Raw values are scaled to comparable mass before blending.
    """
    target = empirical_global_mt(step_index)
    w = EMPIRICAL_BLEND
    pos_keys = [k for k in EMISSION_SECTORS if k != "carbon_removal"]

    sum_raw_pos = sum(max(0.0, float(raw.get(k, 0.0))) for k in pos_keys)
    sum_target_pos = sum(max(0.0, target[k]) for k in pos_keys)

    blended: dict[str, float] = {}
    if sum_raw_pos <= 1e-12:
        for k in pos_keys:
            blended[k] = target[k]
    else:
        scale = sum_target_pos / sum_raw_pos
        for k in pos_keys:
            r = max(0.0, float(raw.get(k, 0.0)))
            scaled = r * scale
            blended[k] = w * target[k] + (1.0 - w) * scaled

    tr = float(target.get("carbon_removal", 0.0))
    rr = float(raw.get("carbon_removal", tr))
    blended["carbon_removal"] = w * tr + (1.0 - w) * rr
    return blended


def ratio_to_1990_baseline(mt: dict[str, float]) -> dict[str, float]:
    """
    For each sector: current Mt / 1990 baseline Mt (same dimensionless ratio as growth factors).
    carbon_removal: mt / BASELINE_CARBON_REMOVAL_MT_1990 (both negative → ratio > 0 when |removal| grows).
    """
    pos_keys = [k for k in EMISSION_SECTORS if k != "carbon_removal"]
    out: dict[str, float] = {}
    for k in pos_keys:
        base = BASE_MT_1990[k]
        if base <= 1e-15:
            out[k] = 1.0
        else:
            out[k] = float(mt.get(k, 0.0)) / base

    denom = BASELINE_CARBON_REMOVAL_MT_1990
    if abs(denom) <= 1e-15:
        out["carbon_removal"] = 1.0
    else:
        out["carbon_removal"] = float(mt.get("carbon_removal", 0.0)) / denom
    return out


