import os
import time
from typing import Any

from openai import AsyncOpenAI

from .cost import RunMetrics, calculate_cost
from .models import Lead, LeadList
from .search import fetch_search_results

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TAVILY_RESULTS = 10


class OrchestratorError(Exception):
    pass


SYSTEM_PROMPT = """
You are an expert B2B telecom lead researcher. Your job is to parse the provided search results 
and extract decision makers relevant to IT, Telecom, VoIP, and Networking.

SCORING GUIDELINES:
- fit_score: 0.0 to 1.0. How well does this person/org match a high-value VoIP prospect?
- evidence_score: 0.0 to 1.0. How current and direct is the source evidence?
- contact_score: 0.0 to 1.0. How usable is the email/phone/title?

GATE LOGIC:
Set gate_passed = True if fit, evidence, and contact scores are all >= 0.6.

EMAIL DEDUCTION:
If emails are not fully visible, deduce them based on common domain patterns if possible.
Set email_status to Found, Deduced, or Missing.

CONTENT:
For each lead, write a specific 1-sentence cold email opener referencing their job title, 
their organization type (school district / government / SMB), and one concrete reason 
a VoIP upgrade matters to them specifically. Make it feel like homework was done.
Include a human-readable explanation of your ranking in the 'explanation' field.
"""


async def scout(
    query: str,
    openai_key: str | None = None,
    tavily_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_leads: int = 15,
    *,
    search_fn=fetch_search_results,
    openai_client: Any | None = None,
) -> tuple[list[Lead], RunMetrics]:
    """Run a Scout query: search + extract + score.

    `search_fn` and `openai_client` are injectable for tests.
    """
    start_time = time.perf_counter()

    api_key = openai_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and openai_client is None:
        raise OrchestratorError("OPENAI_API_KEY not found")

    client = openai_client or AsyncOpenAI(api_key=api_key)

    try:
        search_results = await search_fn(query, api_key=tavily_key, max_results=DEFAULT_TAVILY_RESULTS)
    except Exception as exc:
        raise OrchestratorError(f"Tavily search failed: {exc}") from exc

    try:
        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Target: {query}\n\nSearch Results Data: {search_results}"},
            ],
            response_format=LeadList,
        )
    except Exception as exc:
        raise OrchestratorError(f"OpenAI extraction failed: {exc}") from exc

    try:
        leads_list = completion.choices[0].message.parsed
    except Exception as exc:  # pragma: no cover - defensive branch for SDK drift
        raise OrchestratorError(f"OpenAI response missing parsed LeadList: {exc}") from exc

    leads = leads_list.leads[:max_leads]

    usage = getattr(completion, "usage", None)
    metrics = RunMetrics(
        input_tokens=getattr(usage, "prompt_tokens", 0),
        output_tokens=getattr(usage, "completion_tokens", 0),
        tavily_searches=1,
        elapsed_seconds=round(time.perf_counter() - start_time, 2),
    )
    metrics.estimated_cost_usd = calculate_cost(metrics)

    return leads, metrics
