import asyncio
import os
import time
from collections import Counter
from collections.abc import Mapping
from typing import Any

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .contact_evidence import acquire_contact_evidence
from .coverage import (
    query_plan_from_search_results,
    source_collection_from_search_results,
    write_broad_source_gap_rows,
    write_nonperson_coverage,
)
from .cost import RunMetrics, calculate_cost
from .models import (
    Candidate,
    FailedCandidate,
    Lead,
    LeadList,
    NotFoundCandidate,
    OrganizationOnlyCandidate,
)
from .search import fetch_search_results
from .source_validation import SOURCE_VALIDATION_TIMEOUT_SECONDS, validate_candidate_source

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TAVILY_RESULTS = 50
DEFAULT_FULL_TAVILY_RESULTS = 100
MAX_TAVILY_RESULTS = 500
GATE_THRESHOLD = 0.6
EVIDENCE_GATE_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}
CONTACT_STATUSES = EVIDENCE_GATE_CONTACT_STATUSES | {"missing", "failed", "unsupported"}
OUTPUT_TIERS = ("high_trust_usable", "review", "organization_only", "not_found", "failed")
LEGACY_CONTACT_STATUS_ALIASES = {
    "Found": "verified_found",
    "Deduced": "deduced_with_pattern_evidence",
    "Missing": "missing",
}
MISSING_TEXT_VALUES = {"", "n/a", "na", "none", "null", "unknown", "not available", "unavailable"}


class OrchestratorError(Exception):
    pass


class ExtractedCandidate(BaseModel):
    """Loose LLM extraction row that is converted into strict candidate models."""

    model_config = ConfigDict(extra="forbid")

    candidate_category: str | None = Field(
        default=None,
        description="person_lead, organization_only, not_found, or failed.",
    )
    name: str | None = None
    title: str | None = None
    organization: str | None = None
    email: str | None = None
    email_status: str | None = None
    phone: str | None = None
    phone_status: str | None = None
    source_url: str | None = None
    confidence: float | str | None = None
    why_target: str | None = None
    icebreaker: str | None = None
    fit_score: float | str | None = None
    evidence_score: float | str | None = None
    contact_score: float | str | None = None
    gate_passed: bool | str | None = None
    explanation: str | None = None
    searched_target: str | None = None
    failure_reason: str | None = None


class ExtractedLeadList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    leads: list[ExtractedCandidate] = Field(
        default_factory=list,
        description="Inclusive extracted candidates. Invalid rows are allowed and will be downgraded by the server.",
    )


SYSTEM_PROMPT = """
You are a B2B lead research assistant. Your job is to parse the provided search results
and extract decision makers relevant to the user's query intent.

SCORING GUIDELINES:
- fit_score: 0.0 to 1.0. Query-fit signal only; it does not mean the row is CRM-ready.
- evidence_score: 0.0 to 1.0. Evidence-support signal from current, direct source support.
- contact_score: 0.0 to 1.0. Contact-readiness signal from verified or explicitly supported contact evidence.

GATE:
The gate is a pass/fail summary derived from the three validation signals and supporting validation
evidence. The server will compute and store the final boolean.
Do not describe high fit, evidence, or contact values as "ready" unless the final server
tier is high_trust_usable. Non-usable rows must explain the blocker in plain language.

CANDIDATE CATEGORIES:
- Set candidate_category='person_lead' for a real person with supported name, title, and organization.
- Set candidate_category='organization_only' when the account is found but no usable person is validated.
- Set candidate_category='not_found' when the target was searched but no acceptable contact was found.
- Set candidate_category='failed' when the evidence contradicts or does not support the row.

INCLUSIVE EXTRACTION:
Return every plausible candidate the search results support; do not pre-filter to only
perfect or gate-passing rows. Missing email, partial evidence, blocked pages, or weak
source support should stay visible with explicit statuses or a failed/non-person category.
If a row cannot safely satisfy person_lead requirements, return it as failed with a
specific failure_reason instead of dropping it.
For broad vertical plus geography queries, return as many categorized rows as the
source results support, up to the requested limit. Do not stop at a top-ten list.

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


def _clean_text(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None

    text = str(value).strip()
    if text.lower() in MISSING_TEXT_VALUES:
        return None
    return text


def _score_or_default(value: Any, *, default: float = 0.0) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, score))


def _bool_or_default(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    return default


def _normalize_contact_status(value: Any, *, email: str) -> str:
    status = _clean_text(value)
    if status is not None:
        status = LEGACY_CONTACT_STATUS_ALIASES.get(status, status)
    if status not in CONTACT_STATUSES:
        status = "unsupported"
    if not email and status != "failed":
        return "missing"
    return status


def _extraction_failure_candidate(
    raw: ExtractedCandidate,
    *,
    query: str,
    reason: str,
) -> FailedCandidate:
    searched_target = (
        _clean_text(raw.searched_target)
        or _clean_text(raw.organization)
        or _clean_text(raw.name)
        or _clean_text(raw.title)
        or query
    )
    explanation = _clean_text(raw.explanation) or reason
    return FailedCandidate(
        searched_target=searched_target,
        failure_reason=reason,
        organization=_clean_text(raw.organization),
        source_url=_clean_text(raw.source_url),
        explanation=explanation,
    )


def _coerce_person_lead(raw: ExtractedCandidate, *, query: str) -> Candidate:
    email = _clean_text(raw.email) or ""
    status = _normalize_contact_status(raw.email_status, email=email)
    payload = {
        "candidate_category": "person_lead",
        "name": _clean_text(raw.name),
        "title": _clean_text(raw.title),
        "organization": _clean_text(raw.organization),
        "email": email,
        "email_status": status,
        "source_url": _clean_text(raw.source_url),
        "confidence": _score_or_default(raw.confidence),
        "why_target": _clean_text(raw.why_target),
        "icebreaker": _clean_text(raw.icebreaker),
        "fit_score": _score_or_default(raw.fit_score),
        "evidence_score": _score_or_default(raw.evidence_score),
        "contact_score": _score_or_default(raw.contact_score),
        "gate_passed": _bool_or_default(raw.gate_passed),
        "explanation": _clean_text(raw.explanation),
    }

    try:
        return Lead(**payload)
    except ValidationError as first_error:
        if email:
            retry_payload = {
                **payload,
                "email": "",
                "email_status": "failed",
                "contact_score": 0.0,
                "gate_passed": False,
            }
            try:
                return Lead(**retry_payload)
            except ValidationError:
                pass

        return _extraction_failure_candidate(
            raw,
            query=query,
            reason=f"Could not safely parse person candidate: {first_error.errors()[0]['msg']}",
        )


def _coerce_extracted_candidate(raw: ExtractedCandidate, *, query: str) -> Candidate:
    category = (_clean_text(raw.candidate_category) or "").lower()
    if category in {"organization", "org_only", "account", "account_only"}:
        category = "organization_only"
    if category in {"not found", "not-found", "no_match"}:
        category = "not_found"
    if category not in {"person_lead", "organization_only", "not_found", "failed"}:
        if _clean_text(raw.name) and _clean_text(raw.title) and _clean_text(raw.organization):
            category = "person_lead"
        elif _clean_text(raw.failure_reason):
            category = "failed"
        elif _clean_text(raw.organization):
            category = "organization_only"
        else:
            category = "failed"

    if category == "person_lead":
        return _coerce_person_lead(raw, query=query)

    if category == "organization_only":
        organization = _clean_text(raw.organization)
        if organization:
            return OrganizationOnlyCandidate(
                organization=organization,
                source_url=_clean_text(raw.source_url),
                explanation=_clean_text(raw.explanation)
                or "Organization was found, but no usable person was validated.",
            )
        return _extraction_failure_candidate(
            raw,
            query=query,
            reason="Could not safely parse organization_only candidate: organization is required.",
        )

    if category == "not_found":
        return NotFoundCandidate(
            searched_target=_clean_text(raw.searched_target) or _clean_text(raw.organization) or query,
            organization=_clean_text(raw.organization),
            source_url=_clean_text(raw.source_url),
            explanation=_clean_text(raw.explanation) or "No acceptable contact was found.",
        )

    return FailedCandidate(
        searched_target=(
            _clean_text(raw.searched_target)
            or _clean_text(raw.organization)
            or _clean_text(raw.name)
            or query
        ),
        failure_reason=_clean_text(raw.failure_reason) or "The extracted candidate could not be trusted.",
        organization=_clean_text(raw.organization),
        source_url=_clean_text(raw.source_url),
        explanation=_clean_text(raw.explanation) or "The candidate could not be trusted.",
    )


def _coerce_extracted_leads(parsed: Any, *, query: str) -> list[Candidate]:
    if isinstance(parsed, LeadList):
        return list(parsed.leads)
    if isinstance(parsed, ExtractedLeadList):
        return [_coerce_extracted_candidate(raw, query=query) for raw in parsed.leads]
    if isinstance(parsed, Mapping):
        loose_list = ExtractedLeadList.model_validate(parsed)
        return [_coerce_extracted_candidate(raw, query=query) for raw in loose_list.leads]

    raw_leads = getattr(parsed, "leads", None)
    if raw_leads is not None:
        loose_list = ExtractedLeadList.model_validate({"leads": raw_leads})
        return [_coerce_extracted_candidate(raw, query=query) for raw in loose_list.leads]

    raise OrchestratorError("OpenAI response missing parsed candidate list")


def _extract_candidates_from_completion(completion: Any, *, query: str) -> list[Candidate]:
    try:
        message = completion.choices[0].message
    except Exception as exc:  # pragma: no cover - defensive branch for SDK drift
        raise OrchestratorError(f"OpenAI response missing message: {exc}") from exc

    parsed = getattr(message, "parsed", None)
    if parsed is None:
        content = getattr(message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise OrchestratorError("OpenAI response missing parsed candidate list")
        try:
            parsed = ExtractedLeadList.model_validate_json(content)
        except ValidationError as exc:
            raise OrchestratorError(f"OpenAI response could not be parsed: {exc}") from exc

    try:
        return _coerce_extracted_leads(parsed, query=query)
    except ValidationError as exc:
        raise OrchestratorError(f"OpenAI response could not be parsed: {exc}") from exc


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


def _validation_status(candidate: Candidate, field_name: str) -> str:
    validation = getattr(candidate, "validation", None)
    record = getattr(validation, field_name, None)
    return getattr(record, "status", "unsupported")


def _validation_note(candidate: Candidate, field_name: str) -> str:
    validation = getattr(candidate, "validation", None)
    record = getattr(validation, field_name, None)
    return getattr(record, "notes", "") or ""


def _normalize_failed_reason(reason: str) -> str:
    cleaned = _clean_text(reason) or "Evidence did not support this row."
    if cleaned.startswith(("REVIEW:", "NOT FOUND:", "ORG-ONLY:", "READY:")):
        return cleaned
    return f"REVIEW: rejected row; no hidden usable lead is implied. {cleaned}"


def _failed_from_conflicting_lead(candidate: Lead, *, reason: str) -> FailedCandidate:
    normalized_reason = _normalize_failed_reason(reason)
    return FailedCandidate(
        searched_target=candidate.organization or candidate.name,
        failure_reason=normalized_reason,
        organization=candidate.organization,
        source_url=candidate.source_url,
        explanation=normalized_reason,
        validation=candidate.validation,
        tier="failed",
        primary_filter_reason=normalized_reason,
    )


def _sync_contact_fields_from_validation(candidate: Lead) -> None:
    email_status = _validation_status(candidate, "email")
    if candidate.email_status == "failed" and not candidate.email and email_status in {"missing", "unsupported"}:
        email_status = "failed"
    elif candidate.email_status == "missing" and not candidate.email and email_status == "unsupported":
        email_status = "missing"
    if email_status in CONTACT_STATUSES:
        candidate.email_status = email_status

    if email_status not in EVIDENCE_GATE_CONTACT_STATUSES:
        candidate.email = ""
        candidate.contact_score = min(candidate.contact_score, 0.4)

    if email_status in {"failed", "unsupported", "missing"}:
        candidate.gate_passed = False


def _apply_score_semantics(candidate: Lead) -> None:
    unsupported_field_count = sum(
        1
        for field_name in ("name", "title", "organization", "source")
        if _validation_status(candidate, field_name) != "supported"
    )
    if unsupported_field_count:
        candidate.evidence_score = min(candidate.evidence_score, max(0.0, 0.55 - (0.15 * (unsupported_field_count - 1))))

    email_status = candidate.email_status
    if email_status == "verified_found":
        pass
    elif email_status == "deduced_with_pattern_evidence":
        candidate.contact_score = min(candidate.contact_score, 0.75)
    elif email_status == "missing":
        candidate.contact_score = min(candidate.contact_score, 0.35)
    elif email_status in {"failed", "unsupported"}:
        candidate.contact_score = min(candidate.contact_score, 0.2)


def _conflict_reason(candidate: Lead) -> str | None:
    source_status = _validation_status(candidate, "source")
    if source_status in {"failed", "missing"}:
        return f"Source could not validate the person row: {_validation_note(candidate, 'source')}"

    for field_name in ("name", "title", "organization"):
        status = _validation_status(candidate, field_name)
        if status == "failed":
            return f"{field_name} failed field validation: {_validation_note(candidate, field_name)}"

    name = candidate.name.strip().lower()
    organization = candidate.organization.strip().lower()
    if name == organization or name in organization or organization in name:
        return "Person and organization claims conflict; the name is not distinct from the account."

    return None


def _tier_person_lead(candidate: Lead) -> Lead | FailedCandidate:
    _sync_contact_fields_from_validation(candidate)
    _apply_score_semantics(candidate)
    conflict_reason = _conflict_reason(candidate)
    if conflict_reason is not None:
        return _failed_from_conflicting_lead(candidate, reason=conflict_reason)

    candidate.gate_passed = _lead_passes_evidence_gate(candidate)
    if candidate.gate_passed:
        candidate.tier = "high_trust_usable"
        candidate.primary_filter_reason = "READY: supported person, organization, source, and usable contact cleared the evidence gate."
        return candidate

    email_status = candidate.email_status
    if email_status not in EVIDENCE_GATE_CONTACT_STATUSES:
        candidate.primary_filter_reason = f"REVIEW: contact is {email_status}; row is not CRM-ready."
    elif any(_validation_status(candidate, field_name) != "supported" for field_name in ("name", "title", "organization")):
        candidate.primary_filter_reason = "REVIEW: name, title, or organization lacks direct source support."
    elif _validation_status(candidate, "source") != "supported":
        candidate.primary_filter_reason = "REVIEW: source does not provide enough direct support."
    else:
        candidate.primary_filter_reason = "REVIEW: validation signals did not clear the high-trust evidence gate."

    candidate.tier = "review"
    return candidate


def _tier_nonperson_candidate(candidate: Candidate) -> Candidate:
    if isinstance(candidate, OrganizationOnlyCandidate):
        candidate.tier = "organization_only"
        explanation = candidate.explanation or "Organization was found, but no validated person was ready."
        candidate.primary_filter_reason = (
            explanation
            if explanation.startswith("ORG-ONLY:")
            else f"ORG-ONLY: account found, but no validated person is CRM-ready. {explanation}"
        )
    elif isinstance(candidate, NotFoundCandidate):
        candidate.tier = "not_found"
        explanation = candidate.explanation or "Target was searched, but no acceptable contact was found."
        candidate.primary_filter_reason = (
            explanation
            if explanation.startswith("NOT FOUND:")
            else f"NOT FOUND: searched target, but no acceptable contact was validated. {explanation}"
        )
    elif isinstance(candidate, FailedCandidate):
        candidate.tier = "failed"
        candidate.failure_reason = _normalize_failed_reason(candidate.failure_reason)
        candidate.explanation = _normalize_failed_reason(candidate.explanation)
        candidate.primary_filter_reason = candidate.failure_reason
    return candidate


def _apply_tiering_and_conflict_resolution(candidates: list[Candidate]) -> list[Candidate]:
    tiered: list[Candidate] = []
    for candidate in candidates:
        if isinstance(candidate, Lead):
            tiered.append(_tier_person_lead(candidate))
        else:
            tiered.append(_tier_nonperson_candidate(candidate))
    return tiered


def _tier_distribution(candidates: list[Candidate]) -> dict[str, int]:
    counts = Counter(getattr(candidate, "tier", "review") for candidate in candidates)
    return {tier: counts.get(tier, 0) for tier in OUTPUT_TIERS}


def _contact_quality_pass_count(candidates: list[Candidate]) -> int:
    return sum(
        1
        for candidate in candidates
        if _validation_status(candidate, "email") in EVIDENCE_GATE_CONTACT_STATUSES
    )


def _build_funnel_counts(
    *,
    search_results: Any,
    extracted_candidate_count: int,
    categorized_rows: list[Candidate],
) -> dict[str, int]:
    source_collection = source_collection_from_search_results(search_results)
    raw_vendor_hits = int(getattr(search_results, "raw_result_count", len(search_results)))
    deduped_sources = int(getattr(search_results, "deduped_source_count", len(search_results)))
    source_snapshots = (
        source_collection.returned_source_count
        if source_collection is not None
        else deduped_sources
    )
    tier_counts = _tier_distribution(categorized_rows)

    return {
        "raw_vendor_hits": raw_vendor_hits,
        "deduped_sources": deduped_sources,
        "source_snapshots": source_snapshots,
        "extracted_candidates": extracted_candidate_count,
        "categorized_rows": len(categorized_rows),
        "person_rows": sum(isinstance(candidate, Lead) for candidate in categorized_rows),
        "high_trust_usable_rows": tier_counts["high_trust_usable"],
        "contact_quality_passes": _contact_quality_pass_count(categorized_rows),
    }


def _build_funnel_notes(funnel_counts: dict[str, int], *, max_leads: int) -> list[str]:
    notes: list[str] = []
    if funnel_counts["raw_vendor_hits"] > funnel_counts["deduped_sources"]:
        notes.append(
            f"Deduped {funnel_counts['raw_vendor_hits']} raw vendor hits to "
            f"{funnel_counts['deduped_sources']} unique sources."
        )
    if funnel_counts["extracted_candidates"] > max_leads:
        notes.append(
            f"Capped {funnel_counts['extracted_candidates']} extracted candidates to "
            f"{max_leads} returned rows."
        )
    if funnel_counts["deduped_sources"] > funnel_counts["extracted_candidates"]:
        notes.append(
            "Extraction returned fewer candidates than deduped sources; broad source gap rows preserve "
            "that loss without promoting them to CRM-ready leads."
        )
    if funnel_counts["contact_quality_passes"] == 0 and funnel_counts["categorized_rows"] > 0:
        notes.append("No returned row has verified or source-backed deduced contact evidence.")
    return notes


def _resolve_max_results(max_leads: int, max_results: int | None, *, aggressive_breadth: bool) -> int:
    if max_results is not None:
        resolved = max_results
    elif aggressive_breadth:
        resolved = max(DEFAULT_FULL_TAVILY_RESULTS, max_leads)
    elif max_leads > DEFAULT_TAVILY_RESULTS:
        resolved = min(DEFAULT_FULL_TAVILY_RESULTS, max_leads)
    else:
        resolved = DEFAULT_TAVILY_RESULTS

    if resolved < 1:
        raise OrchestratorError("max_results must be at least 1")
    if resolved > MAX_TAVILY_RESULTS:
        raise OrchestratorError(f"max_results must be {MAX_TAVILY_RESULTS} or less")
    return resolved


async def scout(
    query: str,
    openai_key: str | None = None,
    tavily_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_leads: int = 15,
    max_results: int | None = None,
    *,
    aggressive_breadth: bool = False,
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
    search_max_results = _resolve_max_results(
        max_leads,
        max_results,
        aggressive_breadth=aggressive_breadth,
    )

    try:
        search_kwargs: dict[str, Any] = {
            "api_key": tavily_key,
            "max_results": search_max_results,
            "filters": filters,
        }
        if aggressive_breadth:
            search_kwargs["aggressive_breadth"] = True
        search_results = await search_fn(query, **search_kwargs)
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
            response_format=ExtractedLeadList,
        )
    except Exception as exc:
        raise OrchestratorError(f"OpenAI extraction failed: {exc}") from exc

    extracted_leads = _extract_candidates_from_completion(completion, query=query)

    query_plan = query_plan_from_search_results(search_results)
    source_collection = source_collection_from_search_results(search_results)
    extracted_candidate_count = len(extracted_leads)
    leads = write_nonperson_coverage(
        extracted_leads[:max_leads],
        query_plan=query_plan,
        source_collection=source_collection,
    )
    leads = write_broad_source_gap_rows(
        leads,
        query_plan=query_plan,
        source_collection=source_collection,
        max_candidates=max_leads,
    )

    async with httpx.AsyncClient(
        timeout=SOURCE_VALIDATION_TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as validation_client:
        validations = await asyncio.gather(
            *(validate_candidate_source(candidate, client=validation_client) for candidate in leads)
        )

    for candidate, validation in zip(leads, validations, strict=True):
        candidate.validation = validation

    contact_evidence_stats = await acquire_contact_evidence(
        leads,
        query=query,
        search_fn=search_fn,
        tavily_key=tavily_key,
        filters=filters,
    )
    leads = _apply_tiering_and_conflict_resolution(leads)
    funnel_counts = _build_funnel_counts(
        search_results=search_results,
        extracted_candidate_count=extracted_candidate_count,
        categorized_rows=leads,
    )

    usage = getattr(completion, "usage", None)
    metrics = RunMetrics(
        input_tokens=getattr(usage, "prompt_tokens", 0),
        output_tokens=getattr(usage, "completion_tokens", 0),
        tavily_searches=tavily_searches + contact_evidence_stats.tavily_searches,
        elapsed_seconds=round(time.perf_counter() - start_time, 2),
        tier_distribution=_tier_distribution(leads),
        funnel_counts=funnel_counts,
        funnel_notes=_build_funnel_notes(funnel_counts, max_leads=max_leads),
    )
    if contact_evidence_stats.searched_candidates:
        metrics.funnel_notes.append(
            "Contact evidence pass searched "
            f"{contact_evidence_stats.searched_candidates} promising rows and acquired "
            f"{contact_evidence_stats.acquired_contacts} source-backed contacts."
        )
    if contact_evidence_stats.searched_organizations:
        metrics.funnel_notes.append(
            "Contact evidence pass checked "
            f"{contact_evidence_stats.searched_organizations} organization-only rows for staff/contact sources."
        )
    metrics.estimated_cost_usd = calculate_cost(metrics)

    return leads, metrics
