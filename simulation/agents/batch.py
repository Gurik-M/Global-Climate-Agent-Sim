"""
Single LLM call per decade: composes all agents (defined in separate modules) into one prompt.
"""

import json
from simulation.agents.base import call_llm
from simulation.agents import AGENTS
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


def _build_system_prompt() -> str:
    """Build system prompt from each agent's PROMPT_FRAGMENT."""
    agent_lines = "\n".join(a.PROMPT_FRAGMENT for a in AGENTS)
    return f"""You are simulating one decade of a global socio-climate model.

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
Output only valid JSON, no other text."""


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


def run_batch_agents(region_states: list[tuple[str, dict]], model: str = "gpt-4o-mini") -> dict[str, dict]:
    """
    One LLM call: given (region_name, state) for each region, return for each region
    a dict with keys: citizens, industry, energy, land_use, international, governance
    (each value is a dict of 0–1 floats). Composes all agent definitions from their modules.
    """
    user_parts = []
    for name, state in region_states:
        user_parts.append(f"## {name}\n{json.dumps(state, indent=0)}")
    user_prompt = (
        "Current decade state for each region (all values roughly 0–1 where relevant).\n\n"
        + "\n\n".join(user_parts)
        + "\n\nOutput the full JSON object for all 7 regions with keys: North America, Europe, Africa, South America, Southeast Asia, Asia Major, Australia. Each region: citizens, industry, energy, land_use, international, governance (each with the numeric keys listed in the system prompt)."
    )

    raw = call_llm(_build_system_prompt(), user_prompt, model=model)
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
