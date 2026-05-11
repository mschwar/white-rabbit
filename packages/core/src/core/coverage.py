from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .models import Candidate, NotFoundCandidate, OrganizationOnlyCandidate
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


def source_collection_from_search_results(search_results: Any) -> SourceCollectionSnapshot | None:
    return getattr(search_results, "source_collection", None)


def query_plan_from_search_results(search_results: Any) -> QueryPlan | None:
    return getattr(search_results, "query_plan", None)
