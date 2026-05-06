import os
from typing import Any
import httpx

TAVILY_API_URL = "https://api.tavily.com"
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_TIMEOUT_SECONDS = 30


class TavilySearchError(Exception):
    pass


async def fetch_search_results(
    query: str, 
    api_key: str | None = None, 
    max_results: int = 5,
    search_depth: str = TAVILY_SEARCH_DEPTH
) -> list[dict[str, Any]]:
    """Fetch search results from Tavily."""
    key = api_key or os.environ.get("TAVILY_API_KEY")
    if not key:
        raise TavilySearchError("TAVILY_API_KEY not found in environment or arguments")

    params = {
        "api_key": key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TAVILY_API_URL}/search",
                json=params,
                timeout=TAVILY_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            return _clean_results(data.get("results", []))
        except httpx.HTTPStatusError as exc:
            raise TavilySearchError(f"Tavily API error: {exc.response.status_code} - {exc.response.text}")
        except httpx.TimeoutException:
            raise TavilySearchError(f"Tavily search timed out after {TAVILY_TIMEOUT_SECONDS} seconds")


def _clean_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitize results to keep context window clean."""
    cleaned = []
    for result in results:
        cleaned.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0.0),
        })
    return cleaned
