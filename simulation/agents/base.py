"""Shared LLM call for agents."""

import json
import re
import time
from openai import OpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    RateLimitError,
)

from simulation.config import OPENAI_API_KEY

# OpenAI sometimes returns 400 "could not parse the JSON body" on valid payloads (infra / strict
# parser quirks). Strip C0 controls from prompts since raw U+0000–U+001F in user-visible text can
# also trigger that error on their side.
_CTRL_EXCEPT_WHITESPACE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _sanitize_message_text(text: str) -> str:
    return _CTRL_EXCEPT_WHITESPACE.sub(" ", text)


def _is_retryable_openai_error(exc: BaseException) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError, RateLimitError)):
        return True
    if isinstance(exc, BadRequestError):
        msg = str(exc).lower()
        return "could not parse the json" in msg or "parse the json body" in msg
    return False


def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """Call OpenAI chat completion and return assistant content."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Add it to .env")
    system_prompt = _sanitize_message_text(system_prompt)
    user_prompt = _sanitize_message_text(user_prompt)
    client = OpenAI(api_key=OPENAI_API_KEY)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    last_exc: Exception | None = None
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.4,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            last_exc = e
            if not _is_retryable_openai_error(e) or attempt == 3:
                raise
            time.sleep(0.5 * (2**attempt))
    assert last_exc is not None
    raise last_exc


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
