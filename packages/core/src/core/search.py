import os
from collections.abc import Mapping
from typing import Any

import httpx

TAVILY_API_URL = "https://api.tavily.com"
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_TIMEOUT_SECONDS = 30


class TavilySearchError(Exception):
    pass


def _build_search_query(query: str, filters: Mapping[str, Any] | None) -> str:
    if not filters:
        return query

    filter_bits = []
    for key in sorted(filters):
        value = filters[key]
        if value in (None, "", []):
            continue
        filter_bits.append(f"{key}: {value}")

    if not filter_bits:
        return query

    return f"{query}\n{'; '.join(filter_bits)}"


def _clean_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitize results to keep context window clean."""
    cleaned = []
    for result in results:
        entry: dict[str, Any] = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0.0),
        }

        cleaned.append(entry)
    return cleaned


async def fetch_search_results(
    query: str,
    api_key: str | None = None,
    max_results: int = 10,
    search_depth: str = TAVILY_SEARCH_DEPTH,
    filters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Fetch search results from Tavily via direct HTTP API."""
    key = api_key or os.environ.get("TAVILY_API_KEY")
    if not key:
        raise TavilySearchError("TAVILY_API_KEY not found in environment or arguments")

    search_query = _build_search_query(query, filters)

    params = {
        "api_key": key,
        "query": search_query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
    }

    try:
        async with httpx.AsyncClient(timeout=TAVILY_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{TAVILY_API_URL}/search", json=params)
            response.raise_for_status()
            data = response.json()
            return _clean_results(data.get("results", []))
    except httpx.HTTPStatusError as exc:
        raise TavilySearchError(
            f"Tavily API error: {exc.response.status_code} - {exc.response.text}"
        ) from exc
    except httpx.TimeoutException as exc:
        raise TavilySearchError(
            f"Tavily search timed out after {TAVILY_TIMEOUT_SECONDS} seconds"
        ) from exc
    except Exception as exc:
        raise TavilySearchError(f"Tavily search failed: {exc}") from exc
