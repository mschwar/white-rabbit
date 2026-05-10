import asyncio

import httpx
import pytest

from core import search
from core.query_planner import ARIZONA_K12_TARGET_ACCOUNTS


class FakeResponse:
    def __init__(self, results: list[dict[str, object]], status_code: int = 200, text: str = 'OK') -> None:
        self._results = results
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request('POST', 'https://api.tavily.com/search')
            response = httpx.Response(self.status_code, request=request, text=self.text)
            raise httpx.HTTPStatusError('HTTP error', request=request, response=response)

    def json(self) -> dict[str, object]:
        return {'results': self._results}


class FakeAsyncClient:
    def __init__(
        self,
        outcomes: list[object],
        created_clients: list["FakeAsyncClient"],
        timeout: float | None = None,
        captured_queries: list[str] | None = None,
    ) -> None:
        self.outcomes = outcomes
        self.calls = 0
        self.timeout = timeout
        self.captured_queries = captured_queries
        created_clients.append(self)

    async def __aenter__(self) -> 'FakeAsyncClient':
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post(self, url: str, json: dict[str, object]):
        if self.captured_queries is not None:
            self.captured_queries.append(str(json["query"]))
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_fetch_search_results_retries_once_after_timeout(monkeypatch):
    created_clients: list[FakeAsyncClient] = []
    delays: list[float] = []
    request = httpx.Request('POST', 'https://api.tavily.com/search')
    outcomes = [
        httpx.TimeoutException('timeout', request=request),
        FakeResponse(
            [
                {'title': 'Lead 1', 'url': 'https://example.com/1', 'content': 'content 1', 'score': 0.9},
            ]
        ),
    ]

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def fake_async_client(timeout: float | None = None) -> FakeAsyncClient:
        return FakeAsyncClient(outcomes, created_clients, timeout=timeout)

    monkeypatch.setattr(search.httpx, 'AsyncClient', fake_async_client)
    monkeypatch.setattr(search.asyncio, 'sleep', fake_sleep)

    results = asyncio.run(search.fetch_search_results('Healthcare IT directors in Phoenix', api_key='fake'))

    assert results == [
        {'title': 'Lead 1', 'url': 'https://example.com/1', 'content': 'content 1', 'score': 0.9},
    ]
    assert len(created_clients) == 1
    assert created_clients[0].calls == 2
    assert delays == [0.5]


def test_fetch_search_results_raises_after_three_timeout_attempts(monkeypatch):
    created_clients: list[FakeAsyncClient] = []
    delays: list[float] = []
    request = httpx.Request('POST', 'https://api.tavily.com/search')
    outcomes = [
        httpx.TimeoutException('timeout 1', request=request),
        httpx.TimeoutException('timeout 2', request=request),
        httpx.TimeoutException('timeout 3', request=request),
    ]

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    def fake_async_client(timeout: float | None = None) -> FakeAsyncClient:
        return FakeAsyncClient(outcomes, created_clients, timeout=timeout)

    monkeypatch.setattr(search.httpx, 'AsyncClient', fake_async_client)
    monkeypatch.setattr(search.asyncio, 'sleep', fake_sleep)

    with pytest.raises(search.TavilySearchError, match='after 3 attempts'):
        asyncio.run(search.fetch_search_results('Healthcare IT directors in Phoenix', api_key='fake'))

    assert len(created_clients) == 1
    assert created_clients[0].calls == 3
    assert delays == [0.5, 1.0]


def test_fetch_search_results_decomposes_long_arizona_prompt_into_bounded_queries(monkeypatch):
    created_clients: list[FakeAsyncClient] = []
    captured_queries: list[str] = []
    outcomes = [
        FakeResponse(
            [
                {
                    "title": f"Lead {index}",
                    "url": f"https://example.com/{index}",
                    "content": f"content {index}",
                    "score": 0.9,
                }
            ]
        )
        for index in range(8)
    ]

    long_prompt = (
        "Find the Arizona K-12 VoIP benchmark contacts. "
        "I need technology and telecom decision makers for Mesa, Chandler, Peoria, Gilbert, "
        "Deer Valley, Paradise Valley, Dysart, and Maricopa. "
        "Keep the plan explicit, preserve the named accounts, and do not send the entire prompt "
        "to Tavily. Repeat the district list if needed: Mesa, Chandler, Peoria, Gilbert, "
        "Deer Valley, Paradise Valley, Dysart, Maricopa. "
        "The vendor query must stay under the 400 character Tavily limit even though the input "
        "is intentionally long and noisy. "
        "Do not lose the K-12, IT, VoIP, or Arizona intent while compiling the query."
    )

    async def fake_sleep(delay: float) -> None:
        return None

    def fake_async_client(timeout: float | None = None) -> FakeAsyncClient:
        return FakeAsyncClient(
            outcomes,
            created_clients,
            timeout=timeout,
            captured_queries=captured_queries,
        )

    monkeypatch.setattr(search.httpx, "AsyncClient", fake_async_client)
    monkeypatch.setattr(search.asyncio, "sleep", fake_sleep)

    results = asyncio.run(search.fetch_search_results(long_prompt, api_key="fake", max_results=8))

    assert len(results) == 8
    assert len(created_clients) == 1
    assert created_clients[0].calls == 8
    assert len(captured_queries) == 8
    assert all(len(query) <= 400 for query in captured_queries)
    for account in ARIZONA_K12_TARGET_ACCOUNTS:
        assert any(account.lower() in query.lower() for query in captured_queries)
