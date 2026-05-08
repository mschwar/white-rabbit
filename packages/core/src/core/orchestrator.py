import os
import time
from collections.abc import Mapping
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
You are a B2B lead research assistant. Your job is to parse the provided search results
and extract decision makers relevant to the user's query intent.

SCORING GUIDELINES:
- fit_score: 0.0 to 1.0. How well does this person/org match the user's stated query intent?
- evidence_score: 0.0 to 1.0. How current and direct is the source evidence?
- contact_score: 0.0 to 1.0. How usable is the email/phone/title?

GATE LOGIC:
Set gate_passed = True if fit, evidence, and contact scores are all >= 0.6.

EMAIL DEDUCTION:
If you cannot find an email in the search results, set email='' and email_status='Missing'.
Never invent or guess an email.

CONTENT:
Include the organization name for every lead. If you cannot find a clear organization,
omit the lead entirely.
Set source_url as the URL with the strongest direct evidence of the contact's name,
title, and/or organization. Rank by relevance and recency.
For each lead, write a specific 1-sentence cold email opener referencing their job title,
their organization, and one concrete reason their work aligns with the query intent.
Make it feel like homework was done, not a template.
The 'name' field MUST be a real person's first and last name. Never put a job title or
role description in the name field.
Include a human-readable explanation of your ranking in the 'explanation' field.
"""


def _format_filters(filters: Mapping[str, Any] | None) -> str:
    if not filters:
        return ""

    lines = ["Filters:"]
    for key in sorted(filters):
        value = filters[key]
        if value in (None, "", []):
            continue
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


async def scout(
    query: str,
    openai_key: str | None = None,
    tavily_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_leads: int = 15,
    *,
    filters: Mapping[str, Any] | None = None,
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
        search_results = await search_fn(
            query,
            api_key=tavily_key,
            max_results=DEFAULT_TAVILY_RESULTS,
            filters=filters,
        )
    except Exception as exc:
        raise OrchestratorError(f"Tavily search failed: {exc}") from exc

    filter_context = _format_filters(filters)
    user_message = [f"Target: {query}"]
    if filter_context:
        user_message.extend(["", filter_context])
    user_message.extend(["", f"Search Results Data: {search_results}"])

    try:
        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(user_message)},
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
