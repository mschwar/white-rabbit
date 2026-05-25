from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any
import re
from math import ceil
from urllib.parse import urlparse

from .k12_source_map import K12RosterSeed, collect_k12_roster_sources, load_az_k12_source_map

MAX_TAVILY_QUERY_LENGTH = 400
SAFE_VENDOR_QUERY_LENGTH = 380
PLANNER_RESULTS_PER_VENDOR_QUERY = 20
BROAD_QUERY_MIN_VENDOR_QUERIES = 6
BROAD_QUERY_MAX_VENDOR_QUERIES = 10
AGGRESSIVE_BROAD_QUERY_MIN_VENDOR_QUERIES = 12
AGGRESSIVE_BROAD_QUERY_MAX_VENDOR_QUERIES = 25

ARIZONA_K12_TARGET_ACCOUNTS = (
    "Mesa Public Schools",
    "Chandler Unified School District",
    "Peoria Unified School District",
    "Gilbert Public Schools",
    "Deer Valley Unified School District",
    "Paradise Valley Unified School District",
    "Dysart Unified School District",
    "Maricopa Unified School District",
)

_ARIZONA_K12_ACCOUNT_ALIASES = {
    "Mesa Public Schools": ("mesa public schools", "mesa"),
    "Chandler Unified School District": ("chandler unified school district", "chandler"),
    "Peoria Unified School District": ("peoria unified school district", "peoria"),
    "Gilbert Public Schools": ("gilbert public schools", "gilbert"),
    "Deer Valley Unified School District": ("deer valley unified school district", "deer valley"),
    "Paradise Valley Unified School District": (
        "paradise valley unified school district",
        "paradise valley",
    ),
    "Dysart Unified School District": ("dysart unified school district", "dysart"),
    "Maricopa Unified School District": ("maricopa unified school district", "maricopa"),
}

_ARIZONA_K12_ACCOUNT_DOMAINS = {
    "Mesa Public Schools": ("mpsaz.org", "departments.mpsaz.org"),
    "Chandler Unified School District": ("cusd80.com",),
    "Peoria Unified School District": ("peoriaunified.org",),
    "Gilbert Public Schools": ("gilbertschools.net",),
    "Deer Valley Unified School District": ("dvusd.org",),
    "Paradise Valley Unified School District": ("pvschools.net",),
    "Dysart Unified School District": ("dysart.org",),
    "Maricopa Unified School District": ("musd20.org",),
}

_ROLE_PHRASES = (
    "it directors",
    "it director",
    "technology directors",
    "technology director",
    "director of technology",
    "directors of technology",
    "ciso",
    "cisos",
    "cio",
    "cto",
    "director",
    "manager",
    "operations leader",
    "operations leaders",
    "operations manager",
    "operations vp",
    "vp operations",
    "buyer",
    "buyers",
    "commodity buyer",
    "commodity buyers",
    "procurement",
    "procurement manager",
    "purchasing manager",
    "sourcing manager",
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
    "school districts",
    "public schools",
    "education",
    "financial services",
    "finance",
    "bank",
    "banks",
    "manufacturing",
    "industrial",
    "healthcare",
    "health system",
    "health systems",
    "clinic",
    "clinics",
    "hospital",
    "hospitals",
    "university",
    "college",
    "nonprofit",
    "contractor",
    "contractors",
    "agency",
    "retail",
    "retail lumber",
    "lumber yard",
    "lumber yards",
    "building materials",
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
    "washington",
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
    broad_query: bool = False
    aggressive_breadth: bool = False
    target_raw_results: int = 10
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


def _has_school_context(query: str) -> bool:
    lower = query.lower()
    return any(
        phrase in lower
        for phrase in (
            "school",
            "schools",
            "district",
            "districts",
            "students",
            "k-12",
            "k12",
            "education",
        )
    )


def _looks_like_arizona_k12_benchmark(query: str) -> bool:
    lower = query.lower()
    if "arizona" in lower and ("k-12" in lower or "k12" in lower):
        return True
    if _has_school_context(query) and any(
        alias in lower
        for aliases in _ARIZONA_K12_ACCOUNT_ALIASES.values()
        for alias in aliases
        if " " in alias
    ):
        return True
    return False


def _extract_named_accounts(query: str) -> list[str]:
    lower = query.lower()
    has_school_context = _has_school_context(query)
    matches: list[str] = []
    for account, aliases in _ARIZONA_K12_ACCOUNT_ALIASES.items():
        for alias in aliases:
            if " " not in alias and not has_school_context:
                continue
            if _contains_phrase(lower, alias):
                matches.append(account)
                break
    if matches:
        return _unique_preserve_order(matches)
    if _looks_like_arizona_k12_benchmark(query):
        return list(ARIZONA_K12_TARGET_ACCOUNTS)
    return []


def named_account_aliases(account: str) -> tuple[str, ...]:
    """Return known aliases that can be used to tie sources back to an account."""
    return (account, *_ARIZONA_K12_ACCOUNT_ALIASES.get(account, ()))


def official_domains_for_named_account(account: str) -> tuple[str, ...]:
    """Return known official public domains for a reset named account."""
    return _ARIZONA_K12_ACCOUNT_DOMAINS.get(account, ())


def official_domains_for_organization(organization: str) -> tuple[str, ...]:
    """Return known official public domains matching an organization string."""
    lower = organization.lower()
    for account, aliases in _ARIZONA_K12_ACCOUNT_ALIASES.items():
        names = (account, *aliases)
        if any(alias.lower() in lower for alias in names):
            return official_domains_for_named_account(account)
    return ()


def _build_vendor_query(seed: str, filters: Mapping[str, Any] | None) -> str:
    query = _append_filters(seed, filters)
    if len(query) <= SAFE_VENDOR_QUERY_LENGTH:
        return query

    compact_seed = " ".join(_extract_intent_terms(seed))
    if compact_seed:
        query = _append_filters(compact_seed, filters)
    return _limit_to_chars(query)


def _extract_phrase_group(
    query: str,
    groups: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
    fallback_phrases: tuple[str, ...],
) -> list[str]:
    lower = query.lower()
    expansions: list[str] = []
    for triggers, values in groups:
        if any(_contains_phrase(lower, trigger) for trigger in triggers):
            expansions.extend(values)

    if not expansions:
        expansions.extend(_match_phrases(lower, fallback_phrases))

    return _unique_preserve_order(expansions)


_ROLE_EXPANSION_GROUPS = (
    (
        ("it", "technology", "cio", "cto", "director of technology", "technology director"),
        (
            "IT director",
            "Director of Technology",
            "technology director",
            "CIO",
            "CTO",
            "information technology leader",
        ),
    ),
    (
        ("ciso", "security", "information security"),
        (
            "CISO",
            "chief information security officer",
            "information security director",
            "security leader",
        ),
    ),
    (
        ("operations", "plant manager", "manufacturing operations"),
        (
            "operations leader",
            "VP operations",
            "operations manager",
            "plant manager",
        ),
    ),
    (
        ("buyer", "buyers", "procurement", "purchasing", "sourcing"),
        (
            "commodity buyer",
            "procurement manager",
            "purchasing manager",
            "sourcing manager",
        ),
    ),
)

_VERTICAL_EXPANSION_GROUPS = (
    (
        ("k-12", "k12", "school", "district", "public schools"),
        ("school districts", "public schools", "K-12 education"),
    ),
    (
        ("healthcare", "hospital", "clinic", "health system"),
        ("healthcare organizations", "hospitals", "clinics", "health systems"),
    ),
    (
        ("finance", "financial services", "bank", "credit union"),
        ("financial services firms", "banks", "credit unions", "investment firms"),
    ),
    (
        ("manufacturing", "industrial", "plant"),
        ("manufacturing companies", "industrial companies", "plants", "factories"),
    ),
    (
        ("lumber", "building materials", "retail lumber"),
        ("retail lumber yards", "building materials dealers", "lumber companies"),
    ),
)

_BROAD_SOURCE_QUALIFIERS = (
    "leadership",
    "staff directory",
    "contact",
    "email",
    "directory",
)
_K12_TECH_ROLE_VARIANTS = (
    "Director of Technology",
    "IT Director",
    "CIO",
    "CTO",
    "Technology Services",
    "Information Technology",
)
_ARIZONA_K12_SOURCE_MAP_SEED_LIMIT_PER_ACCOUNT = 3
_SOURCE_FAMILY_QUERY_TERMS = {
    "district_staff_directory": '"staff directory" technology IT director email phone',
    "district_technology_page": '"information technology" "technology services" CIO CTO "director of technology" phone email',
    "district_leadership_page": '"district leadership" "director of information technology" technology phone',
    "district_board_agenda_pdf": 'filetype:pdf "Information Technology" "Technology Officer" email phone',
    "district_contact_page": '"contact" "Information Technology" technology phone email',
    "district_official_homepage": "official district technology contact",
}


def _extract_role_expansions(query: str) -> list[str]:
    return _extract_phrase_group(query, _ROLE_EXPANSION_GROUPS, _ROLE_PHRASES)


def _extract_vertical_expansions(query: str) -> list[str]:
    return _extract_phrase_group(query, _VERTICAL_EXPANSION_GROUPS, _VERTICAL_PHRASES)


def _extract_locations(query: str, filters: Mapping[str, Any] | None) -> list[str]:
    lower = query.lower()
    locations = _match_phrases(lower, _LOCATION_PHRASES)
    if filters:
        for key, value in filters.items():
            if key.lower() in {"location", "city", "state", "region", "geography"} and value:
                locations.append(str(value))
    return _unique_preserve_order(locations)


@lru_cache(maxsize=1)
def _arizona_k12_source_map_seeds() -> tuple[K12RosterSeed, ...]:
    try:
        return tuple(collect_k12_roster_sources(load_az_k12_source_map()))
    except (OSError, KeyError, TypeError, ValueError):
        return ()


def _arizona_source_map_seeds_for_account(account: str) -> list[K12RosterSeed]:
    return [
        seed
        for seed in _arizona_k12_source_map_seeds()
        if seed.district_name == account
    ][:_ARIZONA_K12_SOURCE_MAP_SEED_LIMIT_PER_ACCOUNT]


def _source_family_query_terms(source_family: str) -> str:
    return _SOURCE_FAMILY_QUERY_TERMS.get(source_family, "technology staff directory contact")


def _source_seed_path_terms(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    return re.sub(r"[^A-Za-z0-9]+", " ", path).strip()


def _source_seed_site(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc.lower()
    return ""


def _build_arizona_source_map_query(account: str, seed: K12RosterSeed) -> str:
    source = seed.url.strip()
    terms = _source_family_query_terms(seed.source_family)
    if source.lower().startswith("site:"):
        account_bit = "" if account.lower() in source.lower() else f' "{account}"'
        return _collapse_whitespace(f"{source}{account_bit} Arizona K-12 {terms}")

    site = _source_seed_site(source)
    path_terms = _source_seed_path_terms(source)
    if site:
        return _collapse_whitespace(f'site:{site} "{account}" Arizona K-12 {terms} {path_terms}')
    return _collapse_whitespace(f'"{source}" "{account}" Arizona K-12 {terms}')


def arizona_official_source_queries_for_named_account(account: str) -> tuple[str, ...]:
    """Return official-source-first Arizona K-12 query seeds for a named district."""
    return tuple(
        _build_arizona_source_map_query(account, seed)
        for seed in _arizona_source_map_seeds_for_account(account)
    )


def _is_broad_query(
    query: str,
    filters: Mapping[str, Any] | None,
    named_accounts: list[str],
) -> bool:
    if named_accounts:
        return False

    roles = _extract_role_expansions(query)
    verticals = _extract_vertical_expansions(query)
    locations = _extract_locations(query, filters)

    return bool(roles and (verticals or locations or filters))


def _target_vendor_query_count(max_results: int, *, aggressive_breadth: bool) -> int:
    required_for_cap = max(1, ceil(max_results / PLANNER_RESULTS_PER_VENDOR_QUERY))
    if aggressive_breadth:
        return min(
            AGGRESSIVE_BROAD_QUERY_MAX_VENDOR_QUERIES,
            max(AGGRESSIVE_BROAD_QUERY_MIN_VENDOR_QUERIES, required_for_cap),
        )
    return min(BROAD_QUERY_MAX_VENDOR_QUERIES, max(BROAD_QUERY_MIN_VENDOR_QUERIES, required_for_cap))


def _compile_named_account_queries(
    normalized_query: str,
    filters: Mapping[str, Any],
    named_accounts: list[str],
    max_results: int,
) -> QueryPlan:
    intent_terms = _extract_intent_terms(normalized_query)
    school_context = _has_school_context(normalized_query)
    if school_context:
        intent_terms.extend(["Arizona", "K-12"])
    intent_summary = " ".join(_unique_preserve_order(intent_terms)) if intent_terms else normalized_query
    vendor_query_seeds: list[str] = []

    if school_context:
        for source_index in range(_ARIZONA_K12_SOURCE_MAP_SEED_LIMIT_PER_ACCOUNT):
            for account in named_accounts:
                source_queries = arizona_official_source_queries_for_named_account(account)
                if source_index < len(source_queries):
                    vendor_query_seeds.append(source_queries[source_index])
        # Interleave by query type, not account, so bounded result sets still
        # include at least one official-domain pass for every named district.
        for account in named_accounts:
            for domain in official_domains_for_named_account(account):
                vendor_query_seeds.append(
                    f'site:{domain} "{account}" Arizona technology staff directory email phone'
                )
        for account in named_accounts:
            vendor_query_seeds.append(
                f'{account} Arizona K-12 "{_K12_TECH_ROLE_VARIANTS[0]}" "{_K12_TECH_ROLE_VARIANTS[1]}" staff directory email'
            )
        for account in named_accounts:
            vendor_query_seeds.append(
                f"{account} Arizona K-12 CIO CTO technology services leadership contact"
            )
        for account in named_accounts:
            vendor_query_seeds.append(f"{account} {intent_summary}")
    else:
        for account in named_accounts:
            vendor_query_seeds.append(f"{account} {intent_summary}")

    vendor_queries = [_build_vendor_query(seed, filters) for seed in vendor_query_seeds]

    return QueryPlan(
        original_query=normalized_query,
        vendor_queries=_unique_preserve_order(vendor_queries),
        named_accounts=named_accounts,
        intent_summary=intent_summary,
        broad_query=False,
        target_raw_results=max_results,
        filters=dict(filters),
        notes=[
            f"Decomposed into {len(named_accounts)} named-account searches.",
            "Compiled each account query to stay within the Tavily limit.",
            (
                "Expanded Arizona K-12 named-account searches with source-map official "
                "staff/technology/leadership families before generic role variants."
                if school_context
                else "Used named-account search without K-12-specific source expansion."
            ),
        ],
    )


def _compile_broad_queries(
    normalized_query: str,
    filters: Mapping[str, Any],
    max_results: int,
    *,
    aggressive_breadth: bool,
) -> QueryPlan:
    roles = _extract_role_expansions(normalized_query) or _extract_intent_terms(normalized_query)[:3]
    verticals = _extract_vertical_expansions(normalized_query) or [" ".join(_extract_intent_terms(normalized_query))]
    locations = _extract_locations(normalized_query, filters)
    location_text = " ".join(locations[:2])
    target_query_count = _target_vendor_query_count(max_results, aggressive_breadth=aggressive_breadth)

    seeds = [normalized_query]
    base_seeds: list[str] = []
    for role in roles:
        for vertical in verticals:
            base = _collapse_whitespace(f"{vertical} {role} {location_text}")
            if base:
                base_seeds.append(base)

            if len(base_seeds) >= target_query_count:
                break
        if len(base_seeds) >= target_query_count:
            break

    seeds.extend(base_seeds)

    qualifiers = _BROAD_SOURCE_QUALIFIERS if aggressive_breadth else _BROAD_SOURCE_QUALIFIERS[:2]
    for base in base_seeds:
        for qualifier in qualifiers:
            seeds.append(_collapse_whitespace(f"{base} {qualifier}"))
            if len(seeds) >= target_query_count * 2:
                break
        if len(seeds) >= target_query_count * 2:
            break

    vendor_queries = _unique_preserve_order(
        [_build_vendor_query(seed, filters) for seed in seeds if seed]
    )[:target_query_count]

    return QueryPlan(
        original_query=normalized_query,
        vendor_queries=vendor_queries,
        intent_summary=normalized_query,
        broad_query=True,
        aggressive_breadth=aggressive_breadth,
        target_raw_results=max_results,
        filters=dict(filters),
        notes=[
            f"Expanded broad query into {len(vendor_queries)} search variants.",
            "Used role, vertical, and location breadth without adding unrelated verticals.",
        ],
    )


def compile_query_plan(
    query: str,
    filters: Mapping[str, Any] | None = None,
    *,
    max_results: int = 10,
    aggressive_breadth: bool = False,
) -> QueryPlan:
    normalized_query = _collapse_whitespace(query)
    normalized_filters = _normalize_filters(filters)
    query_with_filters = _append_filters(normalized_query, normalized_filters)
    named_accounts = _extract_named_accounts(normalized_query)

    if named_accounts:
        return _compile_named_account_queries(
            normalized_query,
            normalized_filters,
            named_accounts,
            max_results,
        )

    if _is_broad_query(normalized_query, normalized_filters, named_accounts) and (
        aggressive_breadth or max_results > PLANNER_RESULTS_PER_VENDOR_QUERY
    ):
        return _compile_broad_queries(
            normalized_query,
            normalized_filters,
            max_results,
            aggressive_breadth=aggressive_breadth,
        )

    if len(query_with_filters) <= SAFE_VENDOR_QUERY_LENGTH:
        return QueryPlan(
            original_query=normalized_query,
            vendor_queries=[query_with_filters],
            intent_summary=normalized_query,
            target_raw_results=max_results,
            filters=normalized_filters,
        )

    intent_terms = _extract_intent_terms(normalized_query)
    intent_summary = " ".join(intent_terms) if intent_terms else normalized_query

    compact_query = _build_vendor_query(intent_summary, normalized_filters)
    notes = ["Compacted the prompt to preserve the lead-search intent within the Tavily limit."]
    if compact_query != query_with_filters:
        notes.append("Dropped filler text while keeping role, vertical, and location terms.")

    return QueryPlan(
        original_query=normalized_query,
        vendor_queries=[compact_query],
        intent_summary=intent_summary,
        target_raw_results=max_results,
        filters=normalized_filters,
        notes=notes,
    )
