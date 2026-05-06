import os
import time
from typing import Any

from openai import AsyncOpenAI
from .models import Lead, LeadList
from .search import fetch_search_results
from .cost import RunMetrics, calculate_cost

DEFAULT_MODEL = "gpt-4o-mini"


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
    max_leads: int = 15
) -> tuple[list[Lead], RunMetrics]:
    """Run a Scout query: search + extract + score."""
    start_time = time.perf_counter()
    
    api_key = openai_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise OrchestratorError("OPENAI_API_KEY not found")

    client = AsyncOpenAI(api_key=api_key)
    
    # 1. Search
    search_results = await fetch_search_results(query, api_key=tavily_key, max_results=10)
    
    # 2. Extract and Score
    # We use OpenAI structured outputs (Beta) via response_format
    try:
        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Target: {query}\n\nSearch Results Data: {search_results}"}
            ],
            response_format=LeadList,
        )
    except Exception as exc:
        raise OrchestratorError(f"OpenAI extraction failed: {str(exc)}")

    leads_list = completion.choices[0].message.parsed
    leads = leads_list.leads[:max_leads]
    
    # 3. Metrics
    usage = completion.usage
    metrics = RunMetrics(
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        tavily_searches=1,
        elapsed_seconds=round(time.perf_counter() - start_time, 2)
    )
    metrics.estimated_cost_usd = calculate_cost(metrics)
    
    return leads, metrics
