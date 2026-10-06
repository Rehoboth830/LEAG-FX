"""
LLM-powered Macro/Central Bank Analyst (Phase 9.1, Step 9).

Upgrades the rule-based macro_analyst.py with genuine language-level
reasoning over real knowledge base entries and real current data,
using Google's Gemini API (free tier - Gemini 2.5 Flash).

Includes retry-with-backoff for transient server errors (e.g. 503
UNAVAILABLE under high demand) - a real, expected characteristic of
relying on a free-tier external API, not a design flaw to avoid.
"""

import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

from src.agents.schema import AgentReport
from src.common.logger import get_logger
from src.knowledge_base.query import get_entry

logger = get_logger(__name__)

load_dotenv()

MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2


def _build_prompt(
    current_differential: float, differential_3m_ago: float, differential_12m_ago: float
) -> str:
    fed_entry = get_entry("fed_funds_rate")
    boj_entry = get_entry("boj_policy_rate")
    differential_entry = get_entry("interest_rate_differential")

    knowledge_context = "\n\n".join(
        f"[{e.title}]\n{e.summary}\n{e.why_it_matters_for_usdjpy}"
        for e in [fed_entry, boj_entry, differential_entry]
        if e is not None
    )

    trend_3m = current_differential - differential_3m_ago
    trend_12m = current_differential - differential_12m_ago

    return f"""You are a macro/central bank analyst for a USD/JPY research system.

Background knowledge:
{knowledge_context}

Current real data:
- Current Fed-BOJ interest rate differential: {current_differential:.2f} percentage points
- Change over 3 months: {trend_3m:+.2f}pp
- Change over 12 months: {trend_12m:+.2f}pp

IMPORTANT CONTEXT: prior statistical research on this system found NO significant
same-month or next-month linear correlation between differential CHANGES and
USD/JPY returns (p=0.53, p=0.90). Any high-confidence short-term timing call
would contradict this evidence. Reason primarily about the long-run structural
story, and be explicit about this limitation.

Respond with ONLY valid JSON, no other text, no markdown code fences, in exactly
this structure:
{{"verdict": "buy" or "sell" or "hold", "confidence": <float 0.0-1.0>, "evidence": [<strings>], "risks": [<strings>]}}"""


def analyze(
    current_differential: float, differential_3m_ago: float, differential_12m_ago: float
) -> AgentReport:
    """
    Produces a macro verdict using real Gemini API reasoning. Retries
    on transient server errors (503) with exponential backoff before
    giving up - a free-tier API being occasionally busy is expected,
    not exceptional.

    Raises:
        ValueError: if the API response isn't valid JSON.
        google.genai.errors.ServerError: if all retries are exhausted.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment (.env)")

    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(
        current_differential, differential_3m_ago, differential_12m_ago
    )

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return _parse_response(response.text)
        except genai_errors.ServerError as e:
            last_error = e
            wait_time = INITIAL_BACKOFF_SECONDS * (2**attempt)
            logger.warning(
                f"Gemini API transient error (attempt {attempt+1}/{MAX_RETRIES}): {e}. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)

    logger.error(f"Gemini API failed after {MAX_RETRIES} attempts: {last_error}")
    raise last_error


def _parse_response(response_text: str) -> AgentReport:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        raise ValueError(f"LLM did not return valid JSON: {response_text[:200]}")

    return AgentReport(
        agent="MacroCentralBankAnalyst_LLM",
        verdict=data["verdict"],
        confidence=float(data["confidence"]),
        evidence=data.get("evidence", []),
        risks=data.get("risks", []),
    )
