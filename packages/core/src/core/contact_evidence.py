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
from .query_planner import named_account_aliases, official_domains_for_organization

CONTACT_EVIDENCE_MAX_CANDIDATES = 8
CONTACT_EVIDENCE_MAX_RESULTS = 5
CONTACT_EVIDENCE_MAX_QUERIES_PER_CANDIDATE = 4
USABLE_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
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
    "technology services",
    "administration",
)
_AUTHORITATIVE_SOURCE_TYPES = {
    "staff_directory",
    "leadership_team",
    "department",
    "contact",
    "board_agenda_pdf",
}
_SOURCE_TYPE_PRIORITY = {
    "staff_directory": 0,
    "leadership_team": 1,
    "department": 2,
    "contact": 3,
    "board_agenda_pdf": 4,
    "about": 5,
    "news_press": 6,
    "generic": 7,
}
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
    contact_field: str
    status: str
    value: str
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


def _same_domain(left: str, right: str) -> bool:
    if not left or not right:
        return False
    return left == right or left.endswith(f".{right}") or right.endswith(f".{left}")


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


def _email_domain(email: str) -> str:
    match = _DOMAIN_RE.search(email)
    return match.group(1).lower() if match else ""


def _text_mentions(value: str, needle: str) -> bool:
    return bool(needle) and needle.lower() in value.lower()


def _text_mentions_candidate_name(value: str, candidate: Lead) -> bool:
    if _text_mentions(value, candidate.name):
        return True
    parts = _name_parts(candidate)
    if parts is None:
        return False
    first, last = parts
    lowered = value.lower()
    return first in lowered and last in lowered


def _text_mentions_candidate_organization(value: str, candidate: Lead) -> bool:
    if _text_mentions(value, candidate.organization):
        return True
    lowered = value.lower()
    return any(alias.lower() in lowered for alias in named_account_aliases(candidate.organization))


def _result_mentions_candidate(result_text: str, candidate: Lead) -> bool:
    lowered = result_text.lower()
    title = candidate.title.lower()
    return _text_mentions_candidate_name(result_text, candidate) or (
        _text_mentions_candidate_organization(result_text, candidate) and title in lowered
    )


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
        supports_organization=_text_mentions_candidate_organization(text, candidate),
        has_contact_source_terms=any(term in lowered for term in _CONTACT_SOURCE_TERMS),
        has_email_pattern=any(marker in lowered for marker in _PATTERN_MARKERS),
        conflict=conflict,
    )


def _rank_contact_results(results: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(
        list(results),
        key=lambda result: (
            _SOURCE_TYPE_PRIORITY.get(_detect_page_type(result), 99),
            0 if any(term in _result_text(result).lower() for term in _CONTACT_SOURCE_TERMS) else 1,
            -float(_result_value(result, "score") or 0.0),
        ),
    )


def _candidate_source_domains(candidate: Lead) -> tuple[str, ...]:
    domains: list[str] = []
    for domain in official_domains_for_organization(candidate.organization):
        if domain and domain not in domains:
            domains.append(domain)
    for value in (
        candidate.source_url,
        candidate.validation.source.source_url,
        candidate.validation.organization.source_url,
        candidate.validation.title.source_url,
        candidate.validation.name.source_url,
    ):
        domain = _source_domain(value or "")
        if domain and domain not in domains:
            domains.append(domain)
    return tuple(domains)


def _source_is_authoritative_for_candidate(result: Mapping[str, Any], candidate: Lead) -> bool:
    source_type = _detect_page_type(result)
    result_domain = _source_domain(_result_url(result))
    if any(_same_domain(result_domain, domain) for domain in _candidate_source_domains(candidate)):
        return source_type in _AUTHORITATIVE_SOURCE_TYPES or any(
            term in _result_text(result).lower() for term in _CONTACT_SOURCE_TERMS
        )
    return source_type == "board_agenda_pdf" and _text_mentions_candidate_organization(_result_text(result), candidate)


def _direct_email_is_source_backed(result: Mapping[str, Any], candidate: Lead, *, email: str) -> bool:
    text = _result_text(result)
    lowered = text.lower()
    if not _source_is_authoritative_for_candidate(result, candidate):
        return False

    if _text_mentions_candidate_name(text, candidate):
        return _text_mentions_candidate_organization(text, candidate) or candidate.title.lower() in lowered

    if not _email_matches_person(email, candidate):
        return False
    domain = _email_domain(email)
    if not domain or not _domain_is_source_backed(domain, result, candidate):
        return False
    return (
        _text_mentions_candidate_organization(text, candidate)
        or candidate.title.lower() in lowered
        or any(term in lowered for term in _CONTACT_SOURCE_TERMS)
    )


def _direct_phone_is_source_backed(result: Mapping[str, Any], candidate: Lead) -> bool:
    text = _result_text(result)
    if not _result_mentions_candidate(text, candidate):
        return False
    return _source_is_authoritative_for_candidate(result, candidate)


def _domain_is_source_backed(domain: str, result: Mapping[str, Any], candidate: Lead) -> bool:
    candidate_domains = _candidate_source_domains(candidate)
    return any(_same_domain(domain, candidate_domain) for candidate_domain in candidate_domains)


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
    for result in _rank_contact_results(results):
        text = _result_text(result)
        for match in _EMAIL_RE.finditer(text):
            email = match.group(0).lower()
            if _email_is_generic(email) or not _email_matches_person(email, candidate):
                continue
            if not _direct_email_is_source_backed(result, candidate, email=email):
                continue
            return _ContactEvidence(
                contact_field="email",
                status="verified_found",
                value=email,
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


def _find_direct_phone_evidence(
    results: Iterable[Mapping[str, Any]],
    candidate: Lead,
    *,
    signals: Iterable[_PageSignal] = (),
) -> _ContactEvidence | None:
    signal_list = list(signals)
    corroborating_sources = max(1, _corroborating_source_count(signal_list))
    conflicts = _conflicting_signals(signal_list)
    for result in _rank_contact_results(results):
        text = _result_text(result)
        if not _direct_phone_is_source_backed(result, candidate):
            continue
        for match in _PHONE_RE.finditer(text):
            phone = match.group(0).strip()
            return _ContactEvidence(
                contact_field="phone",
                status="verified_found",
                value=phone,
                source_url=_result_url(result),
                snippet=_snippet(text, phone),
                notes=(
                    "Direct person phone found in targeted public-web evidence pass "
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

    for result in _rank_contact_results(results):
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
        if not _domain_is_source_backed(domain, result, candidate):
            continue
        email = f"{first}.{last}@{domain}"
        return _ContactEvidence(
            contact_field="email",
            status="deduced_with_pattern_evidence",
            value=email,
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
        phone_status = getattr(candidate.validation.phone, "status", "unsupported")
        if email_status in USABLE_CONTACT_STATUSES or phone_status in USABLE_CONTACT_STATUSES:
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
        source_domains = _candidate_source_domains(candidate)
        queries = []
        for domain in source_domains:
            queries.append(f'site:{domain} "{candidate.name}" email phone contact staff directory')
            queries.append(f'site:{domain} "{candidate.name}" "{candidate.organization}" email phone')
            queries.append(f'site:{domain} "{candidate.organization}" "{candidate.title}" staff directory email phone')
            queries.append(f'site:{domain} "{candidate.organization}" technology services leadership email phone')
        queries.extend([
            f'"{candidate.name}" "{candidate.organization}" {candidate.title} email contact staff leadership team directory',
            f'"{candidate.organization}" "{candidate.title}" staff leadership team department directory email',
            f'"{candidate.organization}" "{candidate.name}" board agenda minutes pdf',
            f'"{candidate.organization}" email format contact directory first.last',
            f'"{candidate.name}" "{candidate.organization}" news press release',
        ])
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
    candidate.contact_score = max(candidate.contact_score, 0.75 if evidence.status == "deduced_with_pattern_evidence" else 0.9)
    contact_record = ContactValidationRecord(
        status=evidence.status,  # type: ignore[arg-type]
        source_url=evidence.source_url,
        evidence_snippet=evidence.snippet,
        checked_at=candidate.validation.source.checked_at,
        notes=evidence.notes,
    )
    if evidence.contact_field == "email":
        candidate.email = evidence.value
        candidate.email_status = evidence.status  # type: ignore[assignment]
        candidate.validation.email = contact_record
    else:
        candidate.phone = evidence.value
        candidate.validation.phone = contact_record
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
            f"corroborating_sources={corroborating_sources}; no direct person email or explicit domain pattern found; "
            "no direct person phone found."
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
                ) or _find_direct_phone_evidence(
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
