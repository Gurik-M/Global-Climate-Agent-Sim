"""
Single LLM call per simulation timestep: composes all agents into one prompt.
"""

import json
import math
from simulation.agents.base import call_llm
from simulation.agents import AGENTS
from simulation.emission_calibration import YEARS_PER_STEP
from simulation.initial_state import REGIONAL_BLOCS


def _extract_json(text: str) -> dict:
    """Extract and parse JSON from LLM response (preserves nested structure)."""
    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            pass
    return {}


def _scenario_instruction(scenario: str | None) -> str:
    if scenario == "climate-protection":
        return (
            "\n\nScenario mode — climate-protection: steer each region toward stronger mitigation and "
            "adaptation (higher climate policy ambition, lower fossil lock-in, more conservation and "
            "electrification where consistent with that region's state). Governance should reflect "
            "priority on emissions cuts and resilience over short-term growth alone."
        )
    if scenario == "growth-only":
        return (
            "\n\nScenario mode — growth-only: steer each region toward economic and industrial expansion "
            "(higher industrial intensity and energy demand where plausible; climate policy is secondary "
            "to competitiveness and development). Governance may be weaker on strict regulation."
        )
    return ""


def _build_system_prompt(scenario: str | None = None) -> str:
    """Build system prompt from each agent's PROMPT_FRAGMENT."""
    agent_lines = "\n".join(a.PROMPT_FRAGMENT for a in AGENTS)
    return f"""You are simulating one {YEARS_PER_STEP:g}-year period of a global socio-climate model.

There are 7 regional blocs. For each region, 6 internal "agents" produce outputs (all values 0–1):

{agent_lines}

For each region, first decide the five non-governance agent outputs from that region's state; then choose governance (policy) for that region given those five signals.

Respond with a single JSON object. Top-level keys are the exact region names. Each region's value is an object with keys: "citizens", "industry", "energy", "land_use", "international", "governance". Each of those is an object of numeric values between 0 and 1.

Example shape (use exact region names):
{{
  "North America": {{ "citizens": {{...}}, "industry": {{...}}, "energy": {{...}}, "land_use": {{...}}, "international": {{...}}, "governance": {{...}} }},
  "Europe": {{ ... }},
  ...
}}

Use only the region names: North America, Europe, Africa, South America, Southeast Asia, Asia Major, Australia.
Output only valid JSON, no other text.{_scenario_instruction(scenario)}"""


def _json_safe_for_prompt(obj: object) -> object:
    """Finite numbers only; strict JSON for embedded regional state (OpenAI SDK uses allow_nan=False)."""
    if isinstance(obj, float):
        return 0.0 if not math.isfinite(obj) else float(obj)
    if isinstance(obj, dict):
        return {str(k): _json_safe_for_prompt(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe_for_prompt(x) for x in obj]
    return obj


def _normalize_agent(d: dict, keys: list[str]) -> dict:
    """Ensure dict has all keys, values in [0,1]."""
    if not isinstance(d, dict):
        d = {}
    out = {}
    for k in keys:
        v = d.get(k, 0.5)
        try:
            out[k] = max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            out[k] = 0.5
    return out


def run_batch_agents(
    region_states: list[tuple[str, dict]],
    model: str = "gpt-4o-mini",
    scenario: str | None = None,
) -> dict[str, dict]:
    """
    One LLM call: given (region_name, state) for each region, return for each region
    a dict with keys: citizens, industry, energy, land_use, international, governance
    (each value is a dict of 0–1 floats). Composes all agent definitions from their modules.
    """
    user_parts = []
    for name, state in region_states:
        safe = _json_safe_for_prompt(dict(state))
        user_parts.append(
            f"## {name}\n{json.dumps(safe, ensure_ascii=True, separators=(',', ':'), allow_nan=False, sort_keys=True)}"
        )
    user_prompt = (
        f"Current regional state for this {YEARS_PER_STEP:g}-year step (all values roughly 0–1 where relevant).\n\n"
        + "\n\n".join(user_parts)
        + "\n\nOutput the full JSON object for all 7 regions with keys: North America, Europe, Africa, South America, Southeast Asia, Asia Major, Australia. Each region: citizens, industry, energy, land_use, international, governance (each with the numeric keys listed in the system prompt)."
    )

    raw = call_llm(_build_system_prompt(scenario), user_prompt, model=model)
    data = _extract_json(raw)
    if not isinstance(data, dict):
        data = {}

    result = {}
    for name in REGIONAL_BLOCS:
        region_data = data.get(name, data.get(name.replace(" ", "_"), {}))
        if not isinstance(region_data, dict):
            region_data = {}
        result[name] = {
            agent.NAME: _normalize_agent(region_data.get(agent.NAME, {}), agent.OUTPUT_KEYS)
            for agent in AGENTS
        }
    return result
