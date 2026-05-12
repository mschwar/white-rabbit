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
CONTACT_EVIDENCE_MAX_QUERIES_PER_CANDIDATE = 4
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
_CONFLICT_TERMS = (
    "former",
    "previously",
    "retired",
    "resigned",
    "left ",
    "no longer",
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
    field_corroborations: int = 0
    conflicting_signals: int = 0
    review_to_high_trust_candidates: int = 0


@dataclass(frozen=True, slots=True)
class _ContactEvidence:
    status: str
    email: str
    source_url: str
    snippet: str
    notes: str
    source_type: str
    corroborating_source_count: int = 1
    conflicting_signals: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class _PageSignal:
    source_url: str
    source_type: str
    text: str
    supports_name: bool = False
    supports_title: bool = False
    supports_organization: bool = False
    has_contact_source_terms: bool = False
    has_email_pattern: bool = False
    conflict: str | None = None


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


def _source_domain(value: str) -> str:
    match = re.search(r"https?://(?:www\.)?([^/?#]+)", value.lower())
    return match.group(1) if match else ""


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


def _text_mentions(value: str, needle: str) -> bool:
    return bool(needle) and needle.lower() in value.lower()


def _result_mentions_candidate(result_text: str, candidate: Lead) -> bool:
    lowered = result_text.lower()
    name = candidate.name.lower()
    organization = candidate.organization.lower()
    title = candidate.title.lower()
    return name in lowered or (organization in lowered and title in lowered)


def _detect_page_type(result: Any) -> str:
    text = _result_text(result).lower()
    url = _result_url(result).lower()
    if ".pdf" in url or " board " in f" {text} " or "agenda" in text or "minutes" in text:
        return "board_agenda_pdf"
    if any(term in text or term in url for term in ("staff", "directory", "employee")):
        return "staff_directory"
    if any(term in text or term in url for term in ("leadership", "executive", "administration", "team")):
        return "leadership_team"
    if "department" in text or "department" in url:
        return "department"
    if "contact" in text or "contact" in url:
        return "contact"
    if any(term in text or term in url for term in ("news", "press", "release")):
        return "news_press"
    if "about" in text or "about" in url:
        return "about"
    return "generic"


def _page_signal(result: Mapping[str, Any], candidate: Lead) -> _PageSignal:
    text = _result_text(result)
    lowered = text.lower()
    conflict = None
    if _text_mentions(text, candidate.name) and any(term in lowered for term in _CONFLICT_TERMS):
        conflict = f"Possible stale role signal on {_result_url(result)}."
    return _PageSignal(
        source_url=_result_url(result),
        source_type=_detect_page_type(result),
        text=text,
        supports_name=_text_mentions(text, candidate.name),
        supports_title=_text_mentions(text, candidate.title),
        supports_organization=_text_mentions(text, candidate.organization),
        has_contact_source_terms=any(term in lowered for term in _CONTACT_SOURCE_TERMS),
        has_email_pattern=any(marker in lowered for marker in _PATTERN_MARKERS),
        conflict=conflict,
    )


def _corroborating_source_count(signals: Iterable[_PageSignal]) -> int:
    urls = {
        signal.source_url
        for signal in signals
        if signal.supports_organization and (signal.supports_name or signal.supports_title or signal.has_contact_source_terms)
    }
    return len(urls)


def _field_corroboration_count(signals: Iterable[_PageSignal]) -> int:
    return sum(
        1
        for signal in signals
        if signal.supports_organization and (signal.supports_name or signal.supports_title)
    )


def _conflicting_signals(signals: Iterable[_PageSignal]) -> tuple[str, ...]:
    return tuple(signal.conflict for signal in signals if signal.conflict)


def _find_direct_email_evidence(
    results: Iterable[Mapping[str, Any]],
    candidate: Lead,
    *,
    signals: Iterable[_PageSignal] = (),
) -> _ContactEvidence | None:
    signal_list = list(signals)
    corroborating_sources = max(1, _corroborating_source_count(signal_list))
    conflicts = _conflicting_signals(signal_list)
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
                notes=(
                    "Direct person email found in targeted public-web evidence pass "
                    f"on a {_detect_page_type(result)} source; corroborating_sources={corroborating_sources}."
                ),
                source_type=_detect_page_type(result),
                corroborating_source_count=corroborating_sources,
                conflicting_signals=conflicts,
            )
    return None


def _find_explicit_pattern_evidence(
    results: Iterable[Mapping[str, Any]],
    candidate: Lead,
    *,
    signals: Iterable[_PageSignal] = (),
) -> _ContactEvidence | None:
    parts = _name_parts(candidate)
    if parts is None:
        return None
    first, last = parts
    signal_list = list(signals)
    corroborating_sources = _corroborating_source_count(signal_list)
    conflicts = _conflicting_signals(signal_list)
    if conflicts:
        return None

    for result in results:
        text = _result_text(result)
        lowered = text.lower()
        if candidate.organization.lower() not in lowered:
            continue
        if not any(marker in lowered for marker in _PATTERN_MARKERS):
            continue
        if corroborating_sources < 1:
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
            notes=(
                "Explicit organization email-pattern evidence supports first.last deduction "
                f"from a {_detect_page_type(result)} source; corroborating_sources={corroborating_sources}."
            ),
            source_type=_detect_page_type(result),
            corroborating_source_count=corroborating_sources,
            conflicting_signals=conflicts,
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


def _contact_queries(candidate: Candidate, original_query: str) -> list[str]:
    queries: list[str]
    if isinstance(candidate, Lead):
        domain = _source_domain(candidate.source_url)
        queries = [
            f'"{candidate.name}" "{candidate.organization}" {candidate.title} email contact staff leadership team directory',
            f'"{candidate.organization}" "{candidate.title}" staff leadership team department directory email',
            f'"{candidate.organization}" "{candidate.name}" board agenda minutes pdf',
            f'"{candidate.organization}" email format contact directory first.last',
            f'"{candidate.name}" "{candidate.organization}" news press release',
        ]
        if domain:
            queries.insert(1, f'site:{domain} "{candidate.name}" "{candidate.title}" email contact')
    elif isinstance(candidate, OrganizationOnlyCandidate):
        queries = [
            f'"{candidate.organization}" staff leadership team department directory contact email',
            f'"{candidate.organization}" board agenda minutes pdf leadership',
            f'"{candidate.organization}" about contact department email',
            f'"{candidate.organization}" news press leadership',
            f'"{candidate.organization}" {original_query}',
        ]
    else:
        queries = [original_query]

    deduped: list[str] = []
    for query in queries:
        normalized = " ".join(query.split())
        if normalized not in deduped:
            deduped.append(normalized)
    return deduped[:CONTACT_EVIDENCE_MAX_QUERIES_PER_CANDIDATE]


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
    if evidence.conflicting_signals:
        candidate.validation.source.notes = (
            f"{candidate.validation.source.notes} cross_check_conflicts="
            + " | ".join(evidence.conflicting_signals)
        )


def _record_unacquired_contact_search(candidate: Lead, signals: Iterable[_PageSignal]) -> None:
    signal_list = list(signals)
    source_types = sorted({signal.source_type for signal in signal_list})
    corroborating_sources = _corroborating_source_count(signal_list)
    page_type_note = ", ".join(source_types) if source_types else "no accessible page-type signals"
    candidate.validation.email = ContactValidationRecord(
        status=candidate.validation.email.status,
        source_url=candidate.validation.email.source_url,
        evidence_snippet=candidate.validation.email.evidence_snippet,
        checked_at=candidate.validation.email.checked_at,
        notes=(
            f"{candidate.validation.email.notes} Deep contact pass searched page_types={page_type_note}; "
            f"corroborating_sources={corroborating_sources}; no direct person email or explicit domain pattern found."
        ).strip(),
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
    field_corroborations = 0
    conflicting_signals = 0
    review_to_high_trust_candidates = 0

    for candidate in _rank_candidates(candidates):
        searched_candidates += 1
        if isinstance(candidate, OrganizationOnlyCandidate):
            searched_organizations += 1
        result_list: list[Mapping[str, Any]] = []
        signals: list[_PageSignal] = []
        corroborated_urls: set[str] = set()
        conflict_messages: set[str] = set()
        acquired = False

        for contact_query in _contact_queries(candidate, query):
            try:
                results = await search_fn(
                    contact_query,
                    api_key=tavily_key,
                    max_results=CONTACT_EVIDENCE_MAX_RESULTS,
                    filters=filters,
                )
            except Exception:
                continue

            tavily_searches += int(getattr(results, "tavily_searches", 1) or 1)
            new_results = list(results)
            result_list.extend(new_results)

            if isinstance(candidate, Lead):
                new_signals = [_page_signal(result, candidate) for result in new_results]
                signals.extend(new_signals)
                for signal in new_signals:
                    if (
                        signal.source_url not in corroborated_urls
                        and signal.supports_organization
                        and (signal.supports_name or signal.supports_title)
                    ):
                        corroborated_urls.add(signal.source_url)
                        field_corroborations += 1
                    if signal.conflict and signal.conflict not in conflict_messages:
                        conflict_messages.add(signal.conflict)
                        conflicting_signals += 1
                evidence = _find_direct_email_evidence(
                    result_list,
                    candidate,
                    signals=signals,
                ) or _find_explicit_pattern_evidence(
                    result_list,
                    candidate,
                    signals=signals,
                )
                if evidence is not None:
                    was_missing_contact = getattr(candidate.validation.email, "status", "unsupported") not in USABLE_CONTACT_STATUSES
                    _apply_contact_evidence(candidate, evidence)
                    acquired_contacts += 1
                    if (
                        was_missing_contact
                        and candidate.fit_score >= 0.6
                        and candidate.evidence_score >= 0.6
                        and all(
                            getattr(getattr(candidate.validation, field_name), "status", None) == "supported"
                            for field_name in ("name", "title", "organization", "source")
                        )
                        and not evidence.conflicting_signals
                    ):
                        review_to_high_trust_candidates += 1
                    acquired = True
                    break
            elif isinstance(candidate, OrganizationOnlyCandidate):
                if _apply_organization_evidence(candidate, new_results):
                    break

        if not acquired and isinstance(candidate, Lead) and signals:
            _record_unacquired_contact_search(candidate, signals)
            conflicts = _conflicting_signals(signals)
            if conflicts:
                candidate.validation.source.notes = (
                    f"{candidate.validation.source.notes} cross_check_conflicts="
                    + " | ".join(conflicts)
                )

    return ContactEvidenceStats(
        searched_candidates=searched_candidates,
        tavily_searches=tavily_searches,
        acquired_contacts=acquired_contacts,
        searched_organizations=searched_organizations,
        field_corroborations=field_corroborations,
        conflicting_signals=conflicting_signals,
        review_to_high_trust_candidates=review_to_high_trust_candidates,
    )
