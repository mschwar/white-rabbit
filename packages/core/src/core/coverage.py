from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import Candidate, FailedCandidate, NotFoundCandidate, OrganizationOnlyCandidate
from .query_planner import QueryPlan, named_account_aliases
from .source_collection import CollectedSource, SourceCollectionSnapshot


def _normalize(value: str | None) -> str:
    return " ".join(str(value or "").lower().split())


def _candidate_text(candidate: Candidate) -> str:
    parts = [
        getattr(candidate, "organization", ""),
        getattr(candidate, "searched_target", ""),
        getattr(candidate, "source_url", ""),
    ]
    return _normalize(" ".join(part for part in parts if part))


def _candidate_covers_account(candidate: Candidate, aliases: Iterable[str]) -> bool:
    text = _candidate_text(candidate)
    return any(_normalize(alias) and _normalize(alias) in text for alias in aliases)


def _source_text(source: CollectedSource) -> str:
    return _normalize(f"{source.title} {source.url} {source.content}")


def _source_covers_account(source: CollectedSource, aliases: Iterable[str]) -> bool:
    text = _source_text(source)
    return any(_normalize(alias) and _normalize(alias) in text for alias in aliases)


def _first_source_for_account(
    account: str,
    source_collection: SourceCollectionSnapshot | None,
) -> CollectedSource | None:
    if source_collection is None:
        return None

    aliases = named_account_aliases(account)
    for source in source_collection.sources:
        if _source_covers_account(source, aliases):
            return source
    return None


def write_nonperson_coverage(
    candidates: list[Candidate],
    *,
    query_plan: QueryPlan | None,
    source_collection: SourceCollectionSnapshot | None,
) -> list[Candidate]:
    """Represent named-account obligations that extraction did not return.

    The writer does not promote weak evidence into a person lead. It only appends
    organization-only rows when collected source text mentions the account, or
    not-found rows when the account was searched but no source coverage exists.
    """
    if query_plan is None or not query_plan.named_accounts:
        return candidates

    covered_candidates = list(candidates)
    for account in query_plan.named_accounts:
        aliases = named_account_aliases(account)
        if any(_candidate_covers_account(candidate, aliases) for candidate in covered_candidates):
            continue

        source = _first_source_for_account(account, source_collection)
        if source is not None:
            covered_candidates.append(
                OrganizationOnlyCandidate(
                    organization=account,
                    source_url=source.url or None,
                    explanation=(
                        f"Source coverage was found for {account}, but no usable person lead "
                        "was validated from the collected results."
                    ),
                )
            )
            continue

        covered_candidates.append(
            NotFoundCandidate(
                searched_target=account,
                organization=account,
                explanation=(
                    f"{account} was searched as a named-account obligation, but the collected "
                    "sources did not validate an acceptable person lead."
                ),
            )
        )

    return covered_candidates


def _candidate_source_urls(candidates: Iterable[Candidate]) -> set[str]:
    return {
        _normalize(getattr(candidate, "source_url", None))
        for candidate in candidates
        if _normalize(getattr(candidate, "source_url", None))
    }


def write_broad_source_gap_rows(
    candidates: list[Candidate],
    *,
    query_plan: QueryPlan | None,
    source_collection: SourceCollectionSnapshot | None,
    max_candidates: int,
) -> list[Candidate]:
    """Keep broad collected-source coverage visible without promoting weak rows.

    Broad searches can collect many relevant-looking sources while extraction only
    returns a short list. These gap rows preserve that funnel loss as explicit
    non-CRM-ready rows instead of silently dropping source coverage.
    """
    if query_plan is None or not query_plan.broad_query or source_collection is None:
        return candidates
    if max_candidates <= len(candidates):
        return candidates

    covered = list(candidates)
    seen_urls = _candidate_source_urls(covered)
    for source in source_collection.sources:
        if len(covered) >= max_candidates:
            break
        normalized_url = _normalize(source.url)
        if not normalized_url or normalized_url in seen_urls:
            continue

        searched_target = source.title.strip() or source.url
        covered.append(
            FailedCandidate(
                searched_target=searched_target,
                source_url=source.url,
                failure_reason=(
                    "REVIEW: source collected for the broad target, but no source-supported "
                    "person or account row was extracted; no usable lead is implied."
                ),
                explanation=(
                    "Source coverage exists, but extraction did not produce a validated "
                    "person, organization-only, or not-found row from this source."
                ),
            )
        )
        seen_urls.add(normalized_url)

    return covered


def source_collection_from_search_results(search_results: Any) -> SourceCollectionSnapshot | None:
    return getattr(search_results, "source_collection", None)


def query_plan_from_search_results(search_results: Any) -> QueryPlan | None:
    return getattr(search_results, "query_plan", None)
