import asyncio
import os
import time
from collections.abc import Mapping
from typing import Any

import httpx
from openai import AsyncOpenAI

from .cost import RunMetrics, calculate_cost
from .models import Candidate, Lead, LeadList
from .search import fetch_search_results
from .source_validation import SOURCE_VALIDATION_TIMEOUT_SECONDS, validate_candidate_source

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TAVILY_RESULTS = 10
GATE_THRESHOLD = 0.6
EVIDENCE_GATE_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}


class OrchestratorError(Exception):
    pass


SYSTEM_PROMPT = """
You are a B2B lead research assistant. Your job is to parse the provided search results
and extract decision makers relevant to the user's query intent.

SCORING GUIDELINES:
- fit_score: 0.0 to 1.0. How well does this person/org match the user's stated query intent?
- evidence_score: 0.0 to 1.0. How current and direct is the source evidence?
- contact_score: 0.0 to 1.0. How usable is the email/phone/title?

GATE:
The gate is a pass/fail summary derived from the three scores and supporting validation
evidence. The server will compute and store the final boolean.

CANDIDATE CATEGORIES:
- Set candidate_category='person_lead' for a real person with supported name, title, and organization.
- Set candidate_category='organization_only' when the account is found but no usable person is validated.
- Set candidate_category='not_found' when the target was searched but no acceptable contact was found.
- Set candidate_category='failed' when the evidence contradicts or does not support the row.

ANTI-BIAS RULES:
Treat the user's query intent as the only vertical signal. Do not inject VoIP,
telecom, networking, or product-upgrade language unless the user's query explicitly asks
for it.
Keep every explanation, why_target, and icebreaker aligned to the query's vertical and
organization type.
If you cannot identify a real person's full first and last name, do not invent one;
use organization_only or not_found instead of forcing a person_lead.
Never use placeholders like N/A, Unknown, or a job title in the name field.

EMAIL DEDUCTION:
Use email_status values from this contact-status set:
- verified_found: the email appears directly in the evidence.
- deduced_with_pattern_evidence: the email is inferred from a verified domain or email pattern and you say why.
- missing: no email is present in the evidence.
- failed: the evidence contradicts the email or shows it is wrong, stale, bounced, or inaccessible.
- unsupported: the evidence does not justify a contact status yet.
If you cannot find an email in the search results, set email='' and email_status='missing'.
Never invent or guess an email, and never use the old Found/Deduced labels.

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


def _lead_passes_evidence_gate(candidate: Lead) -> bool:
    validation = getattr(candidate, "validation", None)
    if candidate.candidate_category != "person_lead" or validation is None:
        return False

    if any(
        getattr(getattr(validation, field_name), "status", None) != "supported"
        for field_name in ("name", "title", "organization", "source")
    ):
        return False

    if getattr(getattr(validation, "email", None), "status", None) not in EVIDENCE_GATE_CONTACT_STATUSES:
        return False

    return (
        candidate.fit_score >= GATE_THRESHOLD
        and candidate.evidence_score >= GATE_THRESHOLD
        and candidate.contact_score >= GATE_THRESHOLD
    )


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
) -> tuple[list[Candidate], RunMetrics]:
    """Run a Scout query: search + extract + score.

    `search_fn` and `openai_client` are injectable for tests.
    """
    start_time = time.perf_counter()

    api_key = openai_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and openai_client is None:
        raise OrchestratorError("OPENAI_API_KEY not found")

    client = openai_client or AsyncOpenAI(api_key=api_key, max_retries=2)

    try:
        search_results = await search_fn(
            query,
            api_key=tavily_key,
            max_results=DEFAULT_TAVILY_RESULTS,
            filters=filters,
        )
        tavily_searches = getattr(search_results, "tavily_searches", 1)
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

    async with httpx.AsyncClient(
        timeout=SOURCE_VALIDATION_TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as validation_client:
        validations = await asyncio.gather(
            *(validate_candidate_source(candidate, client=validation_client) for candidate in leads)
        )

    for candidate, validation in zip(leads, validations, strict=True):
        candidate.validation = validation
        if isinstance(candidate, Lead):
            candidate.gate_passed = _lead_passes_evidence_gate(candidate)

    usage = getattr(completion, "usage", None)
    metrics = RunMetrics(
        input_tokens=getattr(usage, "prompt_tokens", 0),
        output_tokens=getattr(usage, "completion_tokens", 0),
        tavily_searches=tavily_searches,
        elapsed_seconds=round(time.perf_counter() - start_time, 2),
    )
    metrics.estimated_cost_usd = calculate_cost(metrics)

    return leads, metrics
