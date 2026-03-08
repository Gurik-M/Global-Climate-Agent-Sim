"""Shared LLM call for agents."""

import json
from openai import OpenAI

from simulation.config import OPENAI_API_KEY


def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI chat completion and return assistant content."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Add it to .env")
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content or ""


def parse_json_response(text: str) -> dict:
    """Extract a single JSON object from LLM response; clamp numeric values to [0,1]."""
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}
    if not isinstance(data, dict):
        data = {}
    # Clamp all numeric values to [0, 1]
    for k, v in list(data.items()):
        if isinstance(v, (int, float)):
            data[k] = max(0.0, min(1.0, float(v)))
    return data


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))
