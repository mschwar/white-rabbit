import asyncio
import os
from math import ceil
from collections.abc import Mapping
from typing import Any

import httpx

from .query_planner import QueryPlan, compile_query_plan
from .source_collection import (
    SourceCollectionSnapshot,
    SourceSnapshotStore,
    build_source_collection_snapshot,
)

TAVILY_API_URL = "https://api.tavily.com"
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_TIMEOUT_SECONDS = 30
TAVILY_MAX_RESULTS_PER_QUERY = 20


class TavilySearchError(Exception):
    pass


class SearchResults(list[dict[str, Any]]):
    def __init__(
        self,
        results: list[dict[str, Any]],
        tavily_searches: int,
        query_plan: QueryPlan | None = None,
        source_collection: SourceCollectionSnapshot | None = None,
    ) -> None:
        super().__init__(results)
        self.tavily_searches = tavily_searches
        self.query_plan = query_plan
        self.source_collection = source_collection


def _clean_results(results: list[dict[str, Any]], *, vendor_query: str) -> list[dict[str, Any]]:
    """Sanitize results to keep context window clean."""
    cleaned = []
    for result in results:
        entry: dict[str, Any] = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0.0),
            "vendor_query": vendor_query,
            "matched_vendor_queries": [vendor_query],
        }

        cleaned.append(entry)
    return cleaned


def _normalize_url(value: str) -> str:
    return value.split("#", 1)[0].rstrip("/").lower()


def _dedupe_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    deduped: list[dict[str, Any]] = []
    for result in results:
        key = (_normalize_url(str(result.get("url", ""))), str(result.get("title", "")).strip().lower())
        if key in seen:
            existing = seen[key]
            for query in result.get("matched_vendor_queries", []):
                if query not in existing["matched_vendor_queries"]:
                    existing["matched_vendor_queries"].append(query)
            continue
        seen[key] = result
        deduped.append(result)
    return deduped


async def _fetch_single_search_results(
    client: httpx.AsyncClient,
    search_query: str,
    api_key: str,
    max_results: int,
    search_depth: str,
) -> list[dict[str, Any]]:
    params = {
        "api_key": api_key,
        "query": search_query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
    }

    for attempt in range(3):
        try:
            response = await client.post(f"{TAVILY_API_URL}/search", json=params)
            response.raise_for_status()
            data = response.json()
            return _clean_results(data.get("results", []), vendor_query=search_query)
        except httpx.HTTPStatusError as exc:
            raise TavilySearchError(
                f"Tavily API error: {exc.response.status_code} - {exc.response.text}"
            ) from exc
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            if attempt == 2:
                raise TavilySearchError(f"Tavily search failed after 3 attempts: {exc}") from exc
            await asyncio.sleep(0.5 * (2**attempt))


async def fetch_search_results(
    query: str,
    api_key: str | None = None,
    max_results: int = 10,
    search_depth: str = TAVILY_SEARCH_DEPTH,
    filters: Mapping[str, Any] | None = None,
    aggressive_breadth: bool = False,
    source_snapshot_store: SourceSnapshotStore | None = None,
) -> list[dict[str, Any]]:
    """Fetch search results from Tavily via direct HTTP API."""
    key = api_key or os.environ.get("TAVILY_API_KEY")
    if not key:
        raise TavilySearchError("TAVILY_API_KEY not found in environment or arguments")

    plan = compile_query_plan(
        query,
        filters=filters,
        max_results=max_results,
        aggressive_breadth=aggressive_breadth,
    )
    vendor_queries = plan.vendor_queries or [query]
    per_query_max_results = min(
        TAVILY_MAX_RESULTS_PER_QUERY,
        max(1, ceil(max_results / len(vendor_queries))),
    )

    try:
        async with httpx.AsyncClient(timeout=TAVILY_TIMEOUT_SECONDS) as client:
            all_results: list[dict[str, Any]] = []
            for search_query in vendor_queries:
                all_results.extend(
                    await _fetch_single_search_results(
                        client,
                        search_query,
                        key,
                        per_query_max_results,
                        search_depth,
                    )
                )
            deduped_results = _dedupe_results(all_results)[:max_results]
            source_collection = build_source_collection_snapshot(
                query=query,
                results=deduped_results,
                requested_max_results=max_results,
                tavily_searches=len(vendor_queries),
                search_depth=search_depth,
                query_plan=plan,
            )
            if source_snapshot_store is not None:
                source_snapshot_store.save(source_collection)
            return SearchResults(
                deduped_results,
                tavily_searches=len(vendor_queries),
                query_plan=plan,
                source_collection=source_collection,
            )
    except TavilySearchError:
        raise
    except Exception as exc:
        raise TavilySearchError(f"Tavily search failed: {exc}") from exc
