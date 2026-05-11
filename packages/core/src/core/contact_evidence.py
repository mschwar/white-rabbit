from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Mapping

from .models import (
    Candidate,
    ContactValidationRecord,
    FieldValidationRecord,
    Lead,
    OrganizationOnlyCandidate,
)

CONTACT_EVIDENCE_MAX_CANDIDATES = 8
CONTACT_EVIDENCE_MAX_RESULTS = 5
USABLE_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_DOMAIN_RE = re.compile(r"@([A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)
_GENERIC_EMAIL_PREFIXES = {
    "admin",
    "careers",
    "contact",
    "hello",
    "help",
    "hr",
    "info",
    "jobs",
    "noreply",
    "no-reply",
    "office",
    "sales",
    "support",
    "webmaster",
}
_CONTACT_SOURCE_TERMS = (
    "staff",
    "leadership",
    "team",
    "directory",
    "department",
    "board agenda",
    "contact",
    "email",
)
_PATTERN_MARKERS = (
    "first.last@",
    "firstname.lastname@",
    "{first}.{last}@",
    "[first].[last]@",
    "first_last@",
    "first initial last@",
)


SearchFn = Callable[..., Awaitable[Iterable[Mapping[str, Any]]]]


@dataclass(frozen=True, slots=True)
class ContactEvidenceStats:
    searched_candidates: int = 0
    tavily_searches: int = 0
    acquired_contacts: int = 0
    searched_organizations: int = 0


@dataclass(frozen=True, slots=True)
class _ContactEvidence:
    status: str
    email: str
    source_url: str
    snippet: str
    notes: str


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _result_value(result: Any, key: str) -> Any:
    if isinstance(result, Mapping):
        return result.get(key)
    return getattr(result, key, None)


def _result_text(result: Any) -> str:
    return " ".join(
        _clean(_result_value(result, key))
        for key in ("title", "content", "url")
        if _has_text(_result_value(result, key))
    )


def _result_url(result: Any) -> str:
    return _clean(_result_value(result, "url")) or "search-result-snippet"


def _snippet(text: str, needle: str, window: int = 120) -> str:
    lowered = text.lower()
    index = lowered.find(needle.lower())
    if index < 0:
        return text[: window * 2].strip()
    start = max(0, index - window)
    end = min(len(text), index + len(needle) + window)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def _name_parts(candidate: Lead) -> tuple[str, str] | None:
    parts = [part for part in re.split(r"[^A-Za-z]+", candidate.name.lower()) if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[-1]


def _email_is_generic(email: str) -> bool:
    local_part = email.split("@", 1)[0].lower()
    return local_part in _GENERIC_EMAIL_PREFIXES


def _email_matches_person(email: str, candidate: Lead) -> bool:
    parts = _name_parts(candidate)
    if parts is None:
        return False
    first, last = parts
    local_part = re.sub(r"[^a-z]", "", email.split("@", 1)[0].lower())
    return last in local_part and (first in local_part or local_part.startswith(f"{first[:1]}{last}"))


def _result_mentions_candidate(result_text: str, candidate: Lead) -> bool:
    lowered = result_text.lower()
    name = candidate.name.lower()
    organization = candidate.organization.lower()
    title = candidate.title.lower()
    return name in lowered or (organization in lowered and title in lowered)


def _find_direct_email_evidence(results: Iterable[Mapping[str, Any]], candidate: Lead) -> _ContactEvidence | None:
    for result in results:
        text = _result_text(result)
        if not _result_mentions_candidate(text, candidate):
            continue
        for match in _EMAIL_RE.finditer(text):
            email = match.group(0).lower()
            if _email_is_generic(email) or not _email_matches_person(email, candidate):
                continue
            return _ContactEvidence(
                status="verified_found",
                email=email,
                source_url=_result_url(result),
                snippet=_snippet(text, email),
                notes="Direct person email found in targeted public-web evidence pass.",
            )
    return None


def _find_explicit_pattern_evidence(results: Iterable[Mapping[str, Any]], candidate: Lead) -> _ContactEvidence | None:
    parts = _name_parts(candidate)
    if parts is None:
        return None
    first, last = parts

    for result in results:
        text = _result_text(result)
        lowered = text.lower()
        if candidate.organization.lower() not in lowered:
            continue
        if not any(marker in lowered for marker in _PATTERN_MARKERS):
            continue
        domain_match = _DOMAIN_RE.search(text)
        if domain_match is None:
            continue
        domain = domain_match.group(1).lower()
        email = f"{first}.{last}@{domain}"
        return _ContactEvidence(
            status="deduced_with_pattern_evidence",
            email=email,
            source_url=_result_url(result),
            snippet=_snippet(text, domain),
            notes="Explicit organization email-pattern evidence supports first.last deduction.",
        )
    return None


def _promising_candidate(candidate: Candidate) -> bool:
    if isinstance(candidate, Lead):
        email_status = getattr(candidate.validation.email, "status", "unsupported")
        if email_status in USABLE_CONTACT_STATUSES:
            return False
        if getattr(candidate.validation.source, "status", "unsupported") in {"failed", "missing"}:
            return False
        supported_identity_fields = sum(
            1
            for field_name in ("name", "title", "organization")
            if getattr(getattr(candidate.validation, field_name), "status", None) == "supported"
        )
        return supported_identity_fields >= 2 or candidate.fit_score >= 0.6

    if isinstance(candidate, OrganizationOnlyCandidate):
        return _has_text(candidate.organization)

    return False


def _contact_query(candidate: Candidate, original_query: str) -> str:
    if isinstance(candidate, Lead):
        return " ".join(
            [
                f'"{candidate.name}"',
                f'"{candidate.organization}"',
                candidate.title,
                "email contact staff leadership team directory",
            ]
        )
    if isinstance(candidate, OrganizationOnlyCandidate):
        return " ".join(
            [
                f'"{candidate.organization}"',
                "staff leadership team department directory contact email",
                original_query,
            ]
        )
    return original_query


def _rank_candidates(candidates: Iterable[Candidate]) -> list[Candidate]:
    return sorted(
        (candidate for candidate in candidates if _promising_candidate(candidate)),
        key=lambda candidate: (
            isinstance(candidate, Lead),
            getattr(candidate, "fit_score", 0.0),
            getattr(candidate, "evidence_score", 0.0),
        ),
        reverse=True,
    )[:CONTACT_EVIDENCE_MAX_CANDIDATES]


def _apply_contact_evidence(candidate: Lead, evidence: _ContactEvidence) -> None:
    candidate.email = evidence.email
    candidate.email_status = evidence.status  # type: ignore[assignment]
    candidate.contact_score = max(candidate.contact_score, 0.75 if evidence.status == "deduced_with_pattern_evidence" else 0.9)
    candidate.validation.email = ContactValidationRecord(
        status=evidence.status,  # type: ignore[arg-type]
        source_url=evidence.source_url,
        evidence_snippet=evidence.snippet,
        checked_at=candidate.validation.source.checked_at,
        notes=evidence.notes,
    )
    if candidate.validation.source.status != "supported":
        candidate.validation.source = FieldValidationRecord(
            status="supported",
            source_url=evidence.source_url,
            evidence_snippet=evidence.snippet,
            checked_at=candidate.validation.email.checked_at,
            notes="Targeted contact-evidence pass found a source-backed contact result.",
        )


def _apply_organization_evidence(candidate: OrganizationOnlyCandidate, results: Iterable[Mapping[str, Any]]) -> bool:
    for result in results:
        text = _result_text(result)
        lowered = text.lower()
        if candidate.organization.lower() not in lowered:
            continue
        if not any(term in lowered for term in _CONTACT_SOURCE_TERMS):
            continue
        source_url = _result_url(result)
        snippet = _snippet(text, candidate.organization)
        checked_at = candidate.validation.source.checked_at
        candidate.validation.organization = FieldValidationRecord(
            status="supported",
            source_url=source_url,
            evidence_snippet=snippet,
            checked_at=checked_at,
            notes="Organization contact/team source found, but no named person was validated.",
        )
        candidate.validation.source = FieldValidationRecord(
            status="supported",
            source_url=source_url,
            evidence_snippet=snippet,
            checked_at=checked_at,
            notes="Targeted contact-evidence pass found an organization-level source only.",
        )
        return True
    return False


async def acquire_contact_evidence(
    candidates: list[Candidate],
    *,
    query: str,
    search_fn: SearchFn,
    tavily_key: str | None,
    filters: Mapping[str, Any] | None = None,
) -> ContactEvidenceStats:
    searched_candidates = 0
    searched_organizations = 0
    tavily_searches = 0
    acquired_contacts = 0

    for candidate in _rank_candidates(candidates):
        contact_query = _contact_query(candidate, query)
        try:
            results = await search_fn(
                contact_query,
                api_key=tavily_key,
                max_results=CONTACT_EVIDENCE_MAX_RESULTS,
                filters=filters,
            )
        except Exception:
            continue

        searched_candidates += 1
        tavily_searches += int(getattr(results, "tavily_searches", 1) or 1)
        result_list = list(results)

        if isinstance(candidate, Lead):
            evidence = _find_direct_email_evidence(result_list, candidate) or _find_explicit_pattern_evidence(
                result_list,
                candidate,
            )
            if evidence is not None:
                _apply_contact_evidence(candidate, evidence)
                acquired_contacts += 1
        elif isinstance(candidate, OrganizationOnlyCandidate):
            searched_organizations += 1
            _apply_organization_evidence(candidate, result_list)

    return ContactEvidenceStats(
        searched_candidates=searched_candidates,
        tavily_searches=tavily_searches,
        acquired_contacts=acquired_contacts,
        searched_organizations=searched_organizations,
    )
