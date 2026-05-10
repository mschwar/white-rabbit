from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from typing import Any
import re

MAX_TAVILY_QUERY_LENGTH = 400
SAFE_VENDOR_QUERY_LENGTH = 380

ARIZONA_K12_TARGET_ACCOUNTS = (
    "Mesa",
    "Chandler",
    "Peoria",
    "Gilbert",
    "Deer Valley",
    "Paradise Valley",
    "Dysart",
    "Maricopa",
)

_ROLE_PHRASES = (
    "it director",
    "technology director",
    "ciso",
    "cio",
    "cto",
    "director",
    "manager",
    "operations leader",
    "operations manager",
    "procurement manager",
    "sales leader",
    "general manager",
    "plant manager",
    "vice president",
    "vp",
    "head of",
    "principal",
    "owner",
    "founder",
    "decision maker",
    "decision makers",
)

_VERTICAL_PHRASES = (
    "k-12",
    "k12",
    "school district",
    "public schools",
    "education",
    "financial services",
    "manufacturing",
    "healthcare",
    "clinic",
    "hospital",
    "university",
    "college",
    "nonprofit",
    "contractor",
    "contractors",
    "agency",
    "retail",
    "hospitality",
    "energy",
    "smb",
    "startup",
)

_DOMAIN_PHRASES = (
    "voip",
    "telecom",
    "telephony",
    "networking",
    "technology",
    "it",
    "communications",
)

_LOCATION_PHRASES = (
    "arizona",
    "new mexico",
    "colorado",
    "texas",
    "new york",
    "illinois",
    "phoenix",
    "albuquerque",
    "santa fe",
    "detroit",
    "california",
    "florida",
    "nevada",
    "utah",
    "kansas",
    "oklahoma",
)


@dataclass(slots=True)
class QueryPlan:
    original_query: str
    vendor_queries: list[str] = field(default_factory=list)
    named_accounts: list[str] = field(default_factory=list)
    intent_summary: str = ""
    filters: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def _collapse_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    if len(phrase) <= 3 and phrase.isalpha():
        return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None
    return phrase in text


def _unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        key = item.lower()
        if not item or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _normalize_filters(filters: Mapping[str, Any] | None) -> dict[str, Any]:
    if not filters:
        return {}

    normalized: dict[str, Any] = {}
    for key in sorted(filters):
        value = filters[key]
        if value in (None, "", []):
            continue
        normalized[key] = value
    return normalized


def _filter_bits(filters: Mapping[str, Any] | None) -> list[str]:
    if not filters:
        return []

    bits: list[str] = []
    for key in sorted(filters):
        value = filters[key]
        if value in (None, "", []):
            continue
        bits.append(f"{key}: {value}")
    return bits


def _append_filters(query: str, filters: Mapping[str, Any] | None) -> str:
    filter_bits = _filter_bits(filters)
    if not filter_bits:
        return _collapse_whitespace(query)
    return _collapse_whitespace(f"{query}; {'; '.join(filter_bits)}")


def _limit_to_chars(text: str, limit: int = SAFE_VENDOR_QUERY_LENGTH) -> str:
    collapsed = _collapse_whitespace(text)
    if len(collapsed) <= limit:
        return collapsed

    words = collapsed.split()
    trimmed: list[str] = []
    for word in words:
        candidate = " ".join(trimmed + [word])
        if len(candidate) > limit:
            break
        trimmed.append(word)

    if not trimmed:
        return collapsed[:limit].rstrip()

    return " ".join(trimmed)


def _match_phrases(text: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if _contains_phrase(text, phrase)]


def _extract_intent_terms(query: str) -> list[str]:
    lower = query.lower()
    terms: list[str] = []
    terms.extend(_match_phrases(lower, _ROLE_PHRASES))
    terms.extend(_match_phrases(lower, _VERTICAL_PHRASES))
    terms.extend(_match_phrases(lower, _DOMAIN_PHRASES))
    terms.extend(_match_phrases(lower, _LOCATION_PHRASES))

    if not terms:
        terms = _collapse_whitespace(query).split()[:8]

    return _unique_preserve_order(terms)


def _looks_like_arizona_k12_benchmark(query: str) -> bool:
    lower = query.lower()
    if "arizona" not in lower:
        return False
    if "k-12" not in lower and "k12" not in lower:
        return False
    if "district" in lower or "target district" in lower or "target districts" in lower:
        return True
    return any(account.lower() in lower for account in ARIZONA_K12_TARGET_ACCOUNTS)


def _extract_named_accounts(query: str) -> list[str]:
    lower = query.lower()
    matches = [account for account in ARIZONA_K12_TARGET_ACCOUNTS if account.lower() in lower]
    if matches:
        return matches
    if _looks_like_arizona_k12_benchmark(query):
        return list(ARIZONA_K12_TARGET_ACCOUNTS)
    return []


def _build_vendor_query(seed: str, filters: Mapping[str, Any] | None) -> str:
    query = _append_filters(seed, filters)
    if len(query) <= SAFE_VENDOR_QUERY_LENGTH:
        return query

    compact_seed = " ".join(_extract_intent_terms(seed))
    if compact_seed:
        query = _append_filters(compact_seed, filters)
    return _limit_to_chars(query)


def compile_query_plan(query: str, filters: Mapping[str, Any] | None = None) -> QueryPlan:
    normalized_query = _collapse_whitespace(query)
    normalized_filters = _normalize_filters(filters)
    query_with_filters = _append_filters(normalized_query, normalized_filters)

    if len(query_with_filters) <= SAFE_VENDOR_QUERY_LENGTH:
        return QueryPlan(
            original_query=normalized_query,
            vendor_queries=[query_with_filters],
            intent_summary=normalized_query,
            filters=normalized_filters,
        )

    intent_terms = _extract_intent_terms(normalized_query)
    intent_summary = " ".join(intent_terms) if intent_terms else normalized_query
    named_accounts = _extract_named_accounts(normalized_query)

    if named_accounts:
        vendor_queries = [
            _build_vendor_query(f"{account} {intent_summary}", normalized_filters)
            for account in named_accounts
        ]
        vendor_queries = _unique_preserve_order(vendor_queries)
        return QueryPlan(
            original_query=normalized_query,
            vendor_queries=vendor_queries,
            named_accounts=named_accounts,
            intent_summary=intent_summary,
            filters=normalized_filters,
            notes=[
                f"Decomposed into {len(vendor_queries)} named-account searches.",
                "Compiled each account query to stay within the Tavily limit.",
            ],
        )

    compact_query = _build_vendor_query(intent_summary, normalized_filters)
    notes = ["Compacted the prompt to preserve the lead-search intent within the Tavily limit."]
    if compact_query != query_with_filters:
        notes.append("Dropped filler text while keeping role, vertical, and location terms.")

    return QueryPlan(
        original_query=normalized_query,
        vendor_queries=[compact_query],
        intent_summary=intent_summary,
        filters=normalized_filters,
        notes=notes,
    )
