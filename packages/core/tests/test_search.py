import asyncio

import httpx
import pytest

from core import search


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
    def __init__(self, outcomes: list[object], created_clients: list['FakeAsyncClient'], timeout: float | None = None) -> None:
        self.outcomes = outcomes
        self.calls = 0
        self.timeout = timeout
        created_clients.append(self)

    async def __aenter__(self) -> 'FakeAsyncClient':
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post(self, url: str, json: dict[str, object]):
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
